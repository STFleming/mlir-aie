from dataclasses import dataclass, field
from typing import Dict, Tuple, List
from .trace_packet import PacketType, TracePacket

@dataclass(frozen=True)
class TraceIdent:
    """ A unique identifier for a trace based on location and type 

        This is used to create a stream of bytes that can be parsed
        separately for each thing being traced.

    """
    loc: Tuple[int,int]
    p_id: int
    p_type: PacketType 

@dataclass
class TraceBuffers:
    """ A collection of all trace buffers """
    buffers: Dict[TraceIdent, List[TracePacket]] = field(default_factory=dict)

    def add(self, p:TracePacket)->None:
        """ Adds a TracePacket to the appropriate buffer """
        ident = TraceIdent(loc=(p.header.src_row, p.header.src_col), 
                           p_id=p.header.p_id,
                           p_type=p.header.p_type)
        if not ident in self.buffers:
            self.buffers[ident] = []

        for payload in p.dwords:
            self.buffers[ident].append(payload)

