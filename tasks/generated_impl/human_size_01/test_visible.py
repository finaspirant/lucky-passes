import pytest
from human_size import human_size

def test_bytes():
    assert human_size(500) == '500 B'

def test_one_kib():
    assert human_size(1024) == '1.0 KiB'

def test_one_and_half_kib():
    assert human_size(1536) == '1.5 KiB'

def test_megabytes():
    assert human_size(123456789) == '117.7 MiB'

def test_negative():
    with pytest.raises(ValueError):
        human_size(-1)
