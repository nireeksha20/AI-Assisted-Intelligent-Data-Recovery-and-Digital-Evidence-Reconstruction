"""
JPEG progressive entropy validation primitives.

This module intentionally separates:
- marker/scan parsing,
- Huffman-table parsing,
- scan-specific entropy decoding.

It is designed for forensic reconstruction: a candidate ordering is
stronger when its entropy stream can be consumed according to the JPEG
frame and SOS parameters and terminates at the next JPEG marker.

Supported:
- Progressive DC initial scans (Ss=0, Se=0, Ah=0)
- Progressive DC refinement scans (Ss=0, Se=0, Ah>0)

AC scans are currently validated structurally rather than by a full
coefficient decoder. This is deliberate: false claims of complete
JPEG decoding are worse than an explicit partial validator.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Dict, List, Optional, Tuple

from .jpeg_huffman import BitReader, decode_huffman_symbol, parse_dht_segment
from .jpeg_stream_parser import parse_jpeg_stream


@dataclass
class FrameComponent:
    component_id: int
    horizontal_sampling: int
    vertical_sampling: int
    quant_table: int


@dataclass
class FrameInfo:
    width: int
    height: int
    precision: int
    components: Dict[int, FrameComponent]
    max_h: int
    max_v: int

    @property
    def mcu_columns(self) -> int:
        return ceil(self.width / (8 * self.max_h))

    @property
    def mcu_rows(self) -> int:
        return ceil(self.height / (8 * self.max_v))


def _marker_payload(data: bytes, marker: dict) -> bytes:
    offset = marker["offset"]
    length = marker.get("segment_length")
    if length is None:
        return b""
    return data[offset + 4: offset + 2 + length]


def parse_frame_info(data: bytes) -> Optional[FrameInfo]:
    markers = parse_jpeg_stream(data)

    sof = next(
        (m for m in markers if m["name"] in {"SOF0", "SOF1", "SOF2"}),
        None,
    )
    if sof is None:
        return None

    payload = _marker_payload(data, sof)
    if len(payload) < 6:
        return None

    precision = payload[0]
    height = int.from_bytes(payload[1:3], "big")
    width = int.from_bytes(payload[3:5], "big")
    component_count = payload[5]

    expected = 6 + 3 * component_count
    if len(payload) < expected:
        return None

    components: Dict[int, FrameComponent] = {}
    pos = 6
    max_h = 0
    max_v = 0

    for _ in range(component_count):
        component_id = payload[pos]
        sampling = payload[pos + 1]
        quant_table = payload[pos + 2]
        pos += 3

        h = sampling >> 4
        v = sampling & 0x0F
        if h == 0 or v == 0:
            return None

        components[component_id] = FrameComponent(
            component_id=component_id,
            horizontal_sampling=h,
            vertical_sampling=v,
            quant_table=quant_table,
        )
        max_h = max(max_h, h)
        max_v = max(max_v, v)

    return FrameInfo(
        width=width,
        height=height,
        precision=precision,
        components=components,
        max_h=max_h,
        max_v=max_v,
    )


def parse_dht_tables(data: bytes) -> Dict[Tuple[int, int], object]:
    """Return the cumulative Huffman tables defined before/through the stream."""
    tables: Dict[Tuple[int, int], object] = {}

    for marker in parse_jpeg_stream(data):
        if marker["name"] != "DHT":
            continue

        segment = data[
            marker["offset"]:
            marker["offset"] + 2 + marker["segment_length"]
        ]

        # A zero-payload DHT (length=2) is structurally harmless but
        # contains no table definitions.
        try:
            parsed = parse_dht_segment(segment)
        except ValueError:
            continue

        for table in parsed:
            tables[(table.table_class, table.table_id)] = table

    return tables


def parse_sos(data: bytes, sos_marker: dict) -> Optional[dict]:
    payload = _marker_payload(data, sos_marker)
    if len(payload) < 4:
        return None

    component_count = payload[0]
    expected = 1 + 2 * component_count + 3
    if len(payload) < expected:
        return None

    components = []
    pos = 1
    for _ in range(component_count):
        component_id = payload[pos]
        selectors = payload[pos + 1]
        pos += 2
        components.append({
            "component_id": component_id,
            "dc_table": selectors >> 4,
            "ac_table": selectors & 0x0F,
        })

    ss = payload[pos]
    se = payload[pos + 1]
    ahal = payload[pos + 2]

    return {
        "components": components,
        "spectral_start": ss,
        "spectral_end": se,
        "successive_high": ahal >> 4,
        "successive_low": ahal & 0x0F,
    }


def _find_entropy_terminator(
    data: bytes,
    start: int,
) -> Tuple[int, Optional[Tuple[int, int]]]:
    """
    Find the first non-stuffed JPEG marker after an entropy segment.

    Returns:
        (absolute_offset, (marker_byte, next_byte)) or
        (len(data), None)
    """
    i = start
    while i < len(data) - 1:
        if data[i] != 0xFF:
            i += 1
            continue

        nxt = data[i + 1]
        if nxt == 0x00:
            i += 2
            continue
        if 0xD0 <= nxt <= 0xD7:
            i += 2
            continue
        return i, (0xFF, nxt)

    return len(data), None


def _receive_extend(value: int, bits: int) -> int:
    if bits == 0:
        return 0
    if value < (1 << (bits - 1)):
        return value - ((1 << bits) - 1)
    return value


def _blocks_for_component(frame: FrameInfo, component_id: int) -> int:
    component = frame.components[component_id]
    return component.horizontal_sampling * component.vertical_sampling


def _decode_dc_initial(
    entropy: bytes,
    scan: dict,
    frame: FrameInfo,
    tables: Dict[Tuple[int, int], object],
    max_symbols: Optional[int] = None,
) -> dict:
    reader = BitReader(entropy)
    predictors = {component_id: 0 for component_id in frame.components}
    decoded_values = 0
    decoded_symbols = 0
    restart_count = 0

    components = scan["components"]
    interleaved = len(components) > 1

    # In an interleaved scan, each MCU carries the component's sampling
    # number of data units. In a non-interleaved DC scan, each MCU carries
    # exactly one data unit.
    if interleaved:
        units_per_mcu = {
            c["component_id"]: _blocks_for_component(frame, c["component_id"])
            for c in components
        }
        mcu_count = frame.mcu_columns * frame.mcu_rows
    else:
        component_id = components[0]["component_id"]
        units_per_mcu = {component_id: 1}
        component = frame.components[component_id]
        cols = ceil(frame.width / (8 * component.horizontal_sampling))
        rows = ceil(frame.height / (8 * component.vertical_sampling))
        mcu_count = cols * rows

    try:
        for _mcu in range(mcu_count):
            for component_spec in components:
                component_id = component_spec["component_id"]
                table_id = component_spec["dc_table"]
                table = tables.get((0, table_id))
                if table is None:
                    return {
                        "valid": False,
                        "status": "missing_dc_huffman_table",
                        "decoded_units": decoded_values,
                        "decoded_symbols": decoded_symbols,
                        "restart_count": restart_count,
                        "error": f"missing DC table {table_id}",
                    }

                for _unit in range(units_per_mcu[component_id]):
                    category = decode_huffman_symbol(reader, table)
                    decoded_symbols += 1

                    if max_symbols is not None and decoded_symbols > max_symbols:
                        return {
                            "valid": False,
                            "status": "symbol_limit",
                            "decoded_units": decoded_values,
                            "decoded_symbols": decoded_symbols,
                            "restart_count": restart_count,
                            "error": "symbol limit reached",
                        }

                    additional = reader.read_bits(category) if category else 0
                    diff = _receive_extend(additional, category)
                    predictors[component_id] += diff
                    decoded_values += 1

                    # The current BitReader raises at restart markers. We
                    # handle the marker at the stream boundary below; a full
                    # DRI-aware decoder can be layered on without changing
                    # this API.
    except (EOFError, ValueError) as exc:
        return {
            "valid": False,
            "status": "entropy_decode_error",
            "decoded_units": decoded_values,
            "decoded_symbols": decoded_symbols,
            "restart_count": restart_count,
            "error": str(exc),
            "byte_position": reader.byte_pos,
            "bit_position": reader.bit_pos,
            "marker": reader.marker,
        }

    # The expected scan should end on the next marker. Byte position may be
    # one byte before the marker because entropy decoding is bit-oriented.
    return {
        "valid": True,
        "status": "dc_initial_decoded",
        "decoded_units": decoded_values,
        "decoded_symbols": decoded_symbols,
        "restart_count": restart_count,
        "byte_position": reader.byte_pos,
        "bit_position": reader.bit_pos,
        "marker": reader.marker,
    }


def _decode_dc_refinement(
    entropy: bytes,
    scan: dict,
    frame: FrameInfo,
) -> dict:
    reader = BitReader(entropy)
    components = scan["components"]

    if len(components) > 1:
        mcu_count = frame.mcu_columns * frame.mcu_rows
        units = sum(
            _blocks_for_component(frame, c["component_id"])
            for c in components
        ) * mcu_count
    else:
        component = frame.components[components[0]["component_id"]]
        cols = ceil(frame.width / (8 * component.horizontal_sampling))
        rows = ceil(frame.height / (8 * component.vertical_sampling))
        units = cols * rows

    try:
        for _ in range(units):
            reader.read_bit()
    except (EOFError, ValueError) as exc:
        return {
            "valid": False,
            "status": "dc_refinement_decode_error",
            "decoded_units": 0,
            "error": str(exc),
            "byte_position": reader.byte_pos,
            "bit_position": reader.bit_pos,
            "marker": reader.marker,
        }

    return {
        "valid": True,
        "status": "dc_refinement_decoded",
        "decoded_units": units,
        "byte_position": reader.byte_pos,
        "bit_position": reader.bit_pos,
        "marker": reader.marker,
    }


def validate_progressive_scans(data: bytes) -> dict:
    """
    Validate progressive scan entropy where a complete decoder is available.

    The result is intentionally evidence-oriented:
    a successful DC decode is a strong consistency signal, not a claim that
    the entire image has been semantically reconstructed.
    """
    frame = parse_frame_info(data)
    if frame is None:
        return {
            "valid": False,
            "status": "missing_or_invalid_frame",
            "scans": [],
        }

    markers = parse_jpeg_stream(data)
    tables: Dict[Tuple[int, int], object] = {}
    scan_results: List[dict] = []

    for index, marker in enumerate(markers):
        if marker["name"] == "DHT":
            segment = data[
                marker["offset"]:
                marker["offset"] + 2 + marker["segment_length"]
            ]
            try:
                for table in parse_dht_segment(segment):
                    tables[(table.table_class, table.table_id)] = table
            except ValueError:
                # Keep going; structural validation will report the scan
                # limitation rather than pretending this table is usable.
                pass
            continue

        if marker["name"] != "SOS":
            continue

        scan = parse_sos(data, marker)
        if scan is None:
            scan_results.append({
                "scan_index": len(scan_results) + 1,
                "valid": False,
                "status": "invalid_sos",
            })
            continue

        entropy_start = marker["offset"] + 2 + marker["segment_length"]
        entropy_end, terminator = _find_entropy_terminator(
            data, entropy_start
        )
        entropy = data[entropy_start:entropy_end]

        if scan["spectral_start"] == 0 and scan["spectral_end"] == 0:
            if scan["successive_high"] == 0:
                result = _decode_dc_initial(
                    entropy, scan, frame, tables
                )
            else:
                result = _decode_dc_refinement(
                    entropy, scan, frame
                )
        else:
            result = {
                "valid": False,
                "status": "ac_entropy_decoder_not_enabled",
                "decoded_units": 0,
            }

        result.update({
            "scan_index": len(scan_results) + 1,
            "sos_offset": marker["offset"],
            "entropy_start": entropy_start,
            "entropy_end": entropy_end,
            "entropy_bytes": len(entropy),
            "terminator": (
                f"FF{terminator[1]:02X}" if terminator else None
            ),
            "scan": scan,
        })
        scan_results.append(result)

    dc_results = [
        r for r in scan_results
        if r["scan"]["spectral_start"] == 0
        and r["scan"]["spectral_end"] == 0
    ]

    return {
        "valid": bool(scan_results) and all(
            r["valid"] or r["status"] == "ac_entropy_decoder_not_enabled"
            for r in scan_results
        ),
        "status": "scan_analysis_complete",
        "frame": {
            "width": frame.width,
            "height": frame.height,
            "precision": frame.precision,
            "component_count": len(frame.components),
            "mcu_columns": frame.mcu_columns,
            "mcu_rows": frame.mcu_rows,
        },
        "scan_count": len(scan_results),
        "dc_scan_count": len(dc_results),
        "dc_scans_valid": all(r["valid"] for r in dc_results) if dc_results else False,
        "scans": scan_results,
    }


def validate_first_dc_scan(data: bytes) -> dict:
    """
    Fast-path validator for reconstruction search.

    It stops after the first SOS entropy interval. This is intentionally
    much cheaper than validating every scan in a candidate at every beam
    expansion.
    """
    frame = parse_frame_info(data)
    if frame is None:
        return {"valid": False, "status": "missing_frame"}

    markers = parse_jpeg_stream(data)
    tables: Dict[Tuple[int, int], object] = {}

    for marker in markers:
        if marker["name"] == "DHT":
            segment = data[
                marker["offset"]:
                marker["offset"] + 2 + marker["segment_length"]
            ]
            try:
                for table in parse_dht_segment(segment):
                    tables[(table.table_class, table.table_id)] = table
            except ValueError:
                pass
            continue

        if marker["name"] != "SOS":
            continue

        scan = parse_sos(data, marker)
        if scan is None:
            return {"valid": False, "status": "invalid_sos"}

        entropy_start = marker["offset"] + 2 + marker["segment_length"]
        entropy_end, terminator = _find_entropy_terminator(
            data, entropy_start
        )

        # No terminating marker means this scan is still incomplete.
        if terminator is None:
            return {
                "valid": False,
                "status": "incomplete_entropy",
                "entropy_bytes": entropy_end - entropy_start,
            }

        if scan["spectral_start"] != 0 or scan["spectral_end"] != 0:
            return {
                "valid": False,
                "status": "first_scan_not_dc",
            }

        if scan["successive_high"] != 0:
            return {
                "valid": False,
                "status": "first_scan_not_dc_initial",
            }

        result = _decode_dc_initial(
            data[entropy_start:entropy_end],
            scan,
            frame,
            tables,
        )
        result.update({
            "sos_offset": marker["offset"],
            "entropy_start": entropy_start,
            "entropy_end": entropy_end,
            "entropy_bytes": entropy_end - entropy_start,
            "terminator": f"FF{terminator[1]:02X}",
        })
        return result

    return {"valid": False, "status": "no_sos"}


def validate_dc_scan_prefix(data: bytes, max_scans: int = 3) -> dict:
    """
    Validate the first `max_scans` progressive DC scans that are complete
    in the candidate stream. AC scans are ignored.
    """
    frame = parse_frame_info(data)
    if frame is None:
        return {"completed": 0, "valid": 0, "invalid": 0, "scans": []}

    markers = parse_jpeg_stream(data)
    tables: Dict[Tuple[int, int], object] = {}
    results = []

    for marker in markers:
        if marker["name"] == "DHT":
            segment = data[
                marker["offset"]:
                marker["offset"] + 2 + marker["segment_length"]
            ]
            try:
                for table in parse_dht_segment(segment):
                    tables[(table.table_class, table.table_id)] = table
            except ValueError:
                pass
            continue

        if marker["name"] != "SOS":
            continue

        scan = parse_sos(data, marker)
        if scan is None:
            continue

        if not (
            scan["spectral_start"] == 0
            and scan["spectral_end"] == 0
        ):
            continue

        entropy_start = marker["offset"] + 2 + marker["segment_length"]
        entropy_end, terminator = _find_entropy_terminator(
            data, entropy_start
        )

        if terminator is None:
            break

        if scan["successive_high"] == 0:
            result = _decode_dc_initial(
                data[entropy_start:entropy_end],
                scan,
                frame,
                tables,
            )
        else:
            result = _decode_dc_refinement(
                data[entropy_start:entropy_end],
                scan,
                frame,
            )

        result["scan_index"] = len(results) + 1
        results.append(result)

        if len(results) >= max_scans:
            break

    return {
        "completed": len(results),
        "valid": sum(1 for r in results if r.get("valid")),
        "invalid": sum(1 for r in results if not r.get("valid")),
        "scans": results,
    }
