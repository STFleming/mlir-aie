from dataclasses import dataclass, field
from typing import List
from enum import Enum
import ctypes
import sys
sys.setrecursionlimit(100000)

def words2bits(words:List[int]):
    """ Take a list of 32-bit words and turn them into a list of binary digits 
        Essentially turns it into our own long bitvector
    """
    bits = []
    for word in words:
        binary_word = bin(word)[2:].zfill(32)
        bits.extend([int(bit) for bit in binary_word])
    return bits

def bits2int(bits:List[int])->int:
    """ From a bitvector produce an integer """
    return sum(bit << (len(bits) - 1 - pos) for pos, bit in enumerate(bits))

def starts_with_opcode(bits:List[int], opcode:List[int])->bool:
    """ Returns true if the bits list starts with the given opcode list """
    sliced = bits[:len(opcode.value)]
    return sliced == opcode.value

class OpCode(Enum):
    START     = [1,1,1,1,0,0,0,0]
    START_ALT = [1,1,1,1,0,1,0,0]
    STOP      = [1,1,0,1,1,1]
    SINGLE0   = [0]
    SINGLE1   = [1,0,0]
    SINGLE2   = [1,0,1]
    MULTIPLE0 = [1,1,0,0]
    MULTIPLE1 = [1,1,0,1,0,0]
    MULTIPLE2 = [1,1,0,1,0,1]
    REPEAT0   = [1,1,1,0]
    REPEAT1   = [1,1,0,1,1,0]
    FILLER    = [1,1,1,1,1,1,1,0]
    SYNC      = [1,1,1,1,1,1,1,1]

@dataclass
class Frame:
    pass

@dataclass
class Start(Frame):
    timer_value:ctypes.c_uint64
    bits:int = 64

@dataclass
class Stop(Frame):
    no_of_cycles: ctypes.c_uint32
    bits:int = 32

@dataclass
class Single0(Frame):
    event: ctypes.c_uint32
    no_of_cycles: ctypes.c_uint32
    bits:int = 8 

@dataclass
class Single1(Frame):
    event: ctypes.c_uint32
    no_of_cycles: ctypes.c_uint32
    bits:int = 16

@dataclass
class Single2(Frame):
    event: ctypes.c_uint32
    no_of_cycles: ctypes.c_uint32
    bits:int = 24 

@dataclass
class Multiple0(Frame):
    events: List[int]
    no_of_cycles: ctypes.c_uint32
    bits:int = 16

@dataclass
class Multiple1(Frame):
    events: List[int]
    no_of_cycles: ctypes.c_uint32
    bits:int = 24

@dataclass
class Multiple2(Frame):
    events: List[int] 
    no_of_cycles: ctypes.c_uint32
    bits:int = 32

@dataclass
class Repeat0(Frame):
    no_of_repeats: ctypes.c_uint32
    bits:int = 8

@dataclass
class Repeat1(Frame):
    no_of_repeats: ctypes.c_uint32
    bits:int = 16

@dataclass
class Filler(Frame):
    bits:int = 8

@dataclass
class Sync(Frame):
    bits:int = 8

def events_list_from_bitvector(bits:List[int], events:List[str]) -> List:
    """ Returns the list of positions where bits are active in a bitvector"""
    indexes = []
    for index, bit in enumerate(bits):
        if bit == 1:
            new_index = 7 - index
            if new_index >= len(events):
                indexes.append(new_index)
            else:
                indexes.append(events[new_index])
    return indexes

def attempt_event_label(bits:List[int], events:List[str]):
    """ Attempts to label the event, if it can't return the event number """
    e = bits2int(bits)
    if e >= len(events):
        return e
    else:
        return events[e]

def parse_frames_bitvector(bits:List[int], frames:List[Frame] = [], events:List[str] = []) -> List[Frame]:
    
    # recursion exit
    if len(bits) == 0:
        return frames

    if starts_with_opcode(bits, OpCode.START):
        f=Start(timer_value=bits2int(bits[8:64]))

    elif starts_with_opcode(bits, OpCode.START_ALT):
        f=Start(timer_value=bits2int(bits[8:64]))

    elif starts_with_opcode(bits, OpCode.STOP):
        f = Stop(no_of_cycles=bits2int(bits[16:32]))

    elif starts_with_opcode(bits, OpCode.SINGLE0):
        f = Single0(event=attempt_event_label(bits[1:4], events), 
                no_of_cycles=bits2int(bits[4:8]))

    elif starts_with_opcode(bits, OpCode.SINGLE1):
        f = Single1(event=attempt_event_label(bits[3:6], events), 
                no_of_cycles=bits2int(bits[6:16]))

    elif starts_with_opcode(bits, OpCode.SINGLE2):
        f = Single2(event=attempt_event_label(bits[3:6], events), 
                no_of_cycles=bits2int(bits[6:24]))

    elif starts_with_opcode(bits, OpCode.MULTIPLE0):
        f = Multiple0(
                events=events_list_from_bitvector(bits[4:12], events),
                no_of_cycles=bits2int(bits[12:16]))

    elif starts_with_opcode(bits, OpCode.MULTIPLE1):
        f = Multiple1(
                events=events_list_from_bitvector(bits[6:14], events),
                no_of_cycles=bits2int(bits[14:24])
                )

    elif starts_with_opcode(bits, OpCode.MULTIPLE2):
        f = Multiple2(
                events=events_list_from_bitvector(bits[6:14], events),
                no_of_cycles=bits2int(bits[14:32])
                )

    elif starts_with_opcode(bits, OpCode.REPEAT0):
        f = Repeat0(
                no_of_repeats=bits2int(bits[4:8]) 
                )

    elif starts_with_opcode(bits, OpCode.REPEAT1):
        f = Repeat1(
                no_of_repeats=bits2int(bits[6:16])
                )

    elif starts_with_opcode(bits, OpCode.FILLER):
        f = Filler()

    elif starts_with_opcode(bits, OpCode.SYNC):
        f = Sync()

    else:
        raise RuntimeError(f"Unable to parse frames, something has gone wrong.")

    frames.append(f)
    parse_frames_bitvector(bits[f.bits:], frames=frames, events=events)

def parse_frames(words:List[int], events:List[str])->List[Frame]:
    bitvector = words2bits(words)
    f = []
    frames = parse_frames_bitvector(bitvector, f, events)
    return f

