from .trace_packet import TracePacket, PacketHeader, PacketType
from typing import List
from .trace_buffers import TraceBuffers, TraceIdent

def extract_bits(number:int, start:int, end:int):
    """
    Extract bits from number, starting from 'start' to 'end'
    """
    mask = (1 << (end - start + 1)) -1
    return (number >> start) & mask

def parse_packets(words:List) -> List[TracePacket]:
    """ Chunks up the list of words into TracePacket data objects """
    packets = []
    
    wordlist = words_cleanup(words)
    for w in range(0, len(words), 8):
        p = TracePacket(
                    header=parse_header(wordlist[w]),
                    dwords=wordlist[w+1:w+7]
                )
        packets.append(p)
    return packets

def parse_header(word:int) -> PacketHeader:
    """ Attempts to construct a PacketHeader object from the header words """
    return PacketHeader(
                p_id=extract_bits(word, 0, 4),
                p_type=PacketType(extract_bits(word, 12, 14)),
                src_row=extract_bits(word, 16, 20),
                src_col=extract_bits(word, 21, 27),
                valid=parity_check_header(word)
            )

def parity_check_header(word:int)->bool:
    """ Does an odd parity check on the packet header"""
    val = 0
    for i in range(32):
        val = val ^ ((word >> i) & 0x1)
    return val == 1

def words_cleanup(words_in:List[str])->List[int]:
    """ Removes any eof newline artifacts and converts the trace words from
    a list of strings to a list of integers """

    # Remove the last element of the list if it cannot be converted to
    # an int
    try:
        last_word = int(words_in[-1])
    except ValueError:
        words_in.pop()

    try:
        res = [int(x) for x in words_in]
    except:
        try:
            res = [int(x,16) for x in words_in]
        except:
            raise ValueError(f"Trace Words are not a decimal integer or hex number")

    return res
