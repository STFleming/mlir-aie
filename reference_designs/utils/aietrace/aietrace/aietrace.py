from dataclasses import dataclass
import argparse
from typing import List
from .word_parser import parse_packets
from .trace_buffers import TraceBuffers
from .trace_frames import parse_frames 
from .perfetto_generation import construct_timeline, generate_perfetto_json
from .utils import frame_occurence_count

def main():
    parser = argparse.ArgumentParser(description="Parses the logtrace of an application")
    parser.add_argument('--input', type=str, required=True, help='The name of the file containing the trace information')
    parser.add_argument('--events', nargs='+', help="A list mapping event labels to slots events are in slot order e.g. --events INSTR_VECTOR KERNEL_START KERNEL_DONE PORT_RUNNING_0 PORT_RUNNING_1 LOCK_STALL LOCK_ACQUIRE LOCK_RELEASE") 
    parser.add_argument('--json', default='trace.json', help='The prefetto compatible json file that gets generated')
    parser.add_argument('--debug', action='store_true', help='Print extra debug information while parsing')

    args = parser.parse_args()
    if args.debug:
        print(f"Processing tracefile: {args.input}")
    
    # process event list
    events = []
    if args.events:
        events = args.events
    if args.debug:
        print(f"Event list {events}")        

    with open(args.input) as fp:
        trace_words = fp.read().split("\n")
        packets = parse_packets(trace_words) 

        tracebuffs = TraceBuffers()
        for p in packets:
            tracebuffs.add(p)

        if args.debug:
            for buff, trace in tracebuffs.buffers.items():
                print(f"Trace found for {buff.p_type} at location {buff.loc}")
                frames = parse_frames(trace, events)
                frame_occurence_count(frames)
                with open(f"{hash(buff)%1000}_timeline.log", "w") as wp:

                    print(f"Writing the list of frames to {hash(buff)%1000}_timeline.log")
                    for f in frames:
                        wp.write(f"{f}\n")

                    print(f"Writing the constructed timeline to {hash(buff)%1000}_timeline.log")
                    wp.write("\n\n")
                    timeline = construct_timeline(frames)

                    # Remove any long stalls at the end of the trace
                    end_stall_count=0
                    for i in reversed(timeline):
                        if i[0] == ['LOCK_STALL']:
                            end_stall_count = end_stall_count + 1
                        else:
                            break
                    timeline = timeline[:len(timeline)-end_stall_count]

                    for event in timeline:
                        wp.write(f"{event}\n")

        generate_perfetto_json(tracebuffs, filename=args.json, events=events)

if __name__ == '__main__':
    main()
