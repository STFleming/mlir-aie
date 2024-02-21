from dataclasses import dataclass
from typing import List
from enum import Enum

class PacketType(Enum):
    CORE = 0
    MEM = 1
    INTFC = 2
    MEMTILE = 3 

@dataclass
class PacketHeader:
    p_id:int
    p_type:PacketType
    src_row:int
    src_col:int
    valid:bool

@dataclass
class TracePacket:
    header:PacketHeader
    dwords: List

