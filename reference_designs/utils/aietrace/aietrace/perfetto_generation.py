from .trace_frames import Frame, Start, Stop, Single0 
from .trace_frames import Single1, Single2, Multiple0 
from .trace_frames import Multiple1, Repeat0, Repeat1
from .trace_frames import Sync 
from .trace_buffers import TraceBuffers, TraceIdent
from .trace_frames import parse_frames
from typing import List, Dict, Tuple
import json
import copy

def construct_timeline(frames:List[Frame])->List[Tuple[List[str],List[int]]]:
    """ From the frames, construct a timeline of events """
    timeline = []
    ts=0
    for f in frames:
        if isinstance(f, Single0) or isinstance(f, Single1) or isinstance(f,Single2):
            new_ts = ts + f.no_of_cycles + 1 
            event = ([f.event], [new_ts, new_ts])            
            timeline.append(event)
        elif isinstance(f, Multiple0) or isinstance(f, Multiple1):
            new_ts = ts + f.no_of_cycles + 1
            event = (f.events, [new_ts, new_ts])
            timeline.append(event)
        elif isinstance(f, Repeat0) or isinstance(f, Repeat1):
            #new_ts = ts + f.no_of_repeats
            #if len(timeline) > 0:
            #    timeline[-1][1][1] = new_ts
            if len(timeline) > 0:
                for i in range(f.no_of_repeats):
                    new_ts = ts + 1
                    nT = copy.deepcopy(timeline[-1])
                    nT[1][0] = new_ts
                    nT[1][1] = new_ts
                    timeline.append(nT)
                    ts = new_ts
        elif isinstance(f, Sync):
            new_ts = ts + 0x3FFFF
        else:
            new_ts = ts
        ts = new_ts
    return timeline

def generate_perfetto_json(buffs:TraceBuffers, filename:str="trace.json", events:List[str]=[])->None:
    """ Generates a perfetto compatible json from the tracebuffers and 
    writes it into the file filename """
    d = generate_perfetto_dict(buffs, events)
    jstr = json.dumps(d, indent=4)
    with open(filename, "w") as fp:
        fp.write(jstr)

def generate_perfetto_dict(buffs:TraceBuffers, events:List[str] = [])->Dict:
    """ Generates a dict from the TraceBuffers that can be outputted as 
    a json object that perfetto can consume """
    ts = 0
    d = []

    for b, trace in buffs.buffers.items():
        d = d + construct_perfetto_process_and_event_threads(b, events)

    for b, trace in buffs.buffers.items():
        timeline = construct_timeline(parse_frames(trace, events))

        # Remove any long stalls at the end of the trace
        end_stall_count=0
        for i in reversed(timeline):
            if i[0] == ['LOCK_STALL']:
                end_stall_count = end_stall_count + 1
            else:
                break
        timeline = timeline[:len(timeline)-end_stall_count]

        for e in timeline:
            d = d + construct_perfetto_events(b, e, events)
            new_ts = d[-1]['ts']
            ts = max(new_ts, ts)

    return d

def construct_perfetto_process_and_event_threads(b:TraceIdent, event_labels:List[str])->List[Dict]:
    """ Creates a separate thread for each of the trace events for a given trace buffer """
    r = []
    r.append(construct_perfetto_buffer_process(b))  
    for index, label in enumerate(event_labels):
        r.append(construct_perfetto_event_thread(b, label, index))
    return r

def construct_perfetto_event_thread(b:TraceIdent, label:str, index:int)->Dict:
    """ Constuct a thread for the given event """
    d = {}
    d['name'] = "thread_name"
    d['ph'] = 'M'
    d['pid'] = get_perfetto_pid(b)
    d['tid'] = index
    d['args'] = {}
    d['args']['name'] = label
    return d

def construct_perfetto_buffer_process(b:TraceIdent)->Dict:
    """ Creates a dict for a perfetto process for a given buffer """
    d = {}
    d['name'] = "process_name"
    d['ph'] = 'M'
    d['pid'] = get_perfetto_pid(b)
    d['args'] = {}
    d['args']['name'] = f"{b.p_type} trace for tile {b.loc}"
    return d


def construct_perfetto_events(b:TraceIdent, events:Tuple[List[str], List[int]], event_labels:List[str])->List[Dict]:
    """ From a timeline event, construct a perfetto event """
    r = []
    for event in events[0]:
        begin = {}
        begin['name'] = event
        begin['ph'] = 'B'
        begin['ts'] = events[1][0]
        begin['pid'] = get_perfetto_pid(b)
        begin['tid'] = event_labels.index(event) 
        begin['args'] = {}
        r.append(begin)
        end = copy.deepcopy(begin)
        end['ph'] = 'E'
        end['ts'] = events[1][1]
        r.append(end)
    return r 

def get_perfetto_pid(b_info:TraceIdent)->int:
    """ From some buffer identity information get a unique pid that is used in perfetto """ 
    return hash(b_info) % 1000
