"""Test cases for the main module."""

from transcribe_me import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_sample():
    """Sample test case."""
    assert 1 + 1 == 2
