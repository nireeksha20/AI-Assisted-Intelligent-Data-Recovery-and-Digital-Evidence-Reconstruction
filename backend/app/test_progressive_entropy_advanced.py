from pathlib import Path

from core.jpeg_progressive_entropy import (
    validate_dc_scan_prefix,
    validate_first_dc_scan,
    validate_progressive_scans,
)


def load_ground_truth():
    return Path("samples/ground_truth_reconstructed.jpg").read_bytes()


def test_first_progressive_dc_scan():
    data = load_ground_truth()
    result = validate_first_dc_scan(data)

    assert result["valid"] is True
    assert result["status"] == "dc_initial_decoded"
    assert result["decoded_units"] > 0
    assert result["terminator"] == "FFC4"


def test_first_three_dc_scans():
    data = load_ground_truth()
    result = validate_dc_scan_prefix(data, max_scans=3)

    assert result["completed"] == 3
    assert result["valid"] == 3
    assert result["invalid"] == 0


def test_full_progressive_analysis():
    data = load_ground_truth()
    result = validate_progressive_scans(data)

    assert result["scan_count"] == 8
    assert result["dc_scans_valid"] is True
