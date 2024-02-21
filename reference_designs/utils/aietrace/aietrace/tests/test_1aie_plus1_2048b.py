from aietrace.word_parser import parse_packets
from aietrace.trace_buffers import TraceBuffers
from aietrace.trace_frames import parse_frames
from aietrace.perfetto_generation import generate_perfetto_json
import os

TEST_DIR = os.path.dirname(__file__)

def test_parse():
    events = ["INST_VECTOR", "KERNEL_START", "KERNEL_DONE",
              "PORT_RUNNING_0", "PORT_RUNNING_1", "LOCK_STALL",
              "LOCK_ACQUIRE", "LOCK_RELEASE"]

    with open(f"{TEST_DIR}/test_traces/1aie_plus1_2048b.txt", "r") as fp:
        packets = parse_packets(fp.read().split("\n"))
        tb = TraceBuffers()
        for p in packets:
            tb.add(p)

        generate_perfetto_json(tb, filename="aie1_plus1_2048b.json", events=events)
