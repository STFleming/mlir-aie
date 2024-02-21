from .trace_frames import Frame, Start, Stop, Single0
from .trace_frames import Single1, Single2, Multiple0
from .trace_frames import Multiple1, Repeat0, Repeat1
from typing import List
from collections import Counter

def frame_occurence_count(frames:List[Frame])->None:
    """ Reports the number of occurences of each frame type """
    frame_count = Counter(type(frame).__name__ for frame in frames)
    for frame_name, count in frame_count.items():
        print(f'{frame_name}: {count}')
