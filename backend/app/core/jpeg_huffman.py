from dataclasses import dataclass


@dataclass
class HuffmanTable:
    table_class: int
    table_id: int
    codes: dict


def parse_dht_segment(segment: bytes):
    """
    Parse one or more JPEG DHT table definitions.

    segment must include:
        FF C4 + 2-byte length + payload
    """

    if len(segment) < 4 or segment[0:2] != b"\xFF\xC4":
        raise ValueError("Invalid DHT segment")

    segment_length = int.from_bytes(segment[2:4], "big")

    if segment_length < 2:
        raise ValueError("Invalid DHT length")

    payload_end = 2 + segment_length

    if payload_end > len(segment):
        raise ValueError("Incomplete DHT segment")

    pos = 4
    tables = []

    while pos < payload_end:

        if pos >= len(segment):
            break

        info = segment[pos]
        pos += 1

        table_class = (info >> 4) & 0x0F
        table_id = info & 0x0F

        if table_class not in (0, 1):
            raise ValueError("Invalid Huffman table class")

        if table_id > 3:
            raise ValueError("Invalid Huffman table ID")

        if pos + 16 > payload_end:
            raise ValueError("Incomplete DHT code counts")

        counts = list(segment[pos:pos + 16])
        pos += 16

        symbol_count = sum(counts)

        if pos + symbol_count > payload_end:
            raise ValueError("Incomplete DHT symbols")

        symbols = list(segment[pos:pos + symbol_count])
        pos += symbol_count

        codes = {}

        code = 0
        symbol_index = 0

        for bit_length in range(1, 17):

            count = counts[bit_length - 1]

            for _ in range(count):
                symbol = symbols[symbol_index]
                symbol_index += 1

                codes[(code, bit_length)] = symbol
                code += 1

            code <<= 1

        tables.append(
            HuffmanTable(
                table_class=table_class,
                table_id=table_id,
                codes=codes,
            )
        )

    return tables


class BitReader:
    """
    JPEG entropy bit reader.

    Handles:
      FF 00  -> literal FF data byte
      FF D0-D7 -> restart marker
      FF xx   -> JPEG marker
    """

    def __init__(self, data: bytes):
        self.data = data
        self.byte_pos = 0
        self.bit_pos = 0
        self.marker = None

    def _next_data_byte(self):
        if self.byte_pos >= len(self.data):
            raise EOFError("End of entropy data")

        byte = self.data[self.byte_pos]
        self.byte_pos += 1

        if byte != 0xFF:
            return byte

        if self.byte_pos >= len(self.data):
            raise EOFError("Incomplete FF marker")

        next_byte = self.data[self.byte_pos]

        # JPEG byte stuffing.
        if next_byte == 0x00:
            self.byte_pos += 1
            return 0xFF

        # Restart marker.
        if 0xD0 <= next_byte <= 0xD7:
            self.byte_pos += 1
            self.marker = next_byte
            raise EOFError(
                f"Restart marker RST{next_byte - 0xD0}"
            )

        # Any other FF xx is a JPEG marker.
        self.byte_pos += 1
        self.marker = next_byte

        raise EOFError(
            f"JPEG marker 0xFF{next_byte:02X}"
        )

    def read_bit(self):
        if self.bit_pos == 0:
            self.current_byte = self._next_data_byte()

        bit = (
            self.current_byte
            >> (7 - self.bit_pos)
        ) & 1

        self.bit_pos += 1

        if self.bit_pos == 8:
            self.bit_pos = 0

        return bit

    def read_bits(self, count: int):
        value = 0

        for _ in range(count):
            value = (value << 1) | self.read_bit()

        return value


def decode_huffman_symbol(reader: BitReader, table: HuffmanTable):
    """
    Decode one Huffman symbol.

    Returns:
        symbol

    Raises:
        ValueError if no valid Huffman code is found.
    """

    code = 0

    for bit_length in range(1, 17):

        bit = reader.read_bit()
        code = (code << 1) | bit

        symbol = table.codes.get((code, bit_length))

        if symbol is not None:
            return symbol

    raise ValueError("Invalid JPEG Huffman code")