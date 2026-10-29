import pytest
from text_justify import text_justify

def test_example():
    assert text_justify(["This", "is", "an", "example", "of", "text", "justification."], 16) == ['This    is    an', 'example  of text', 'justification.  ']

def test_single_word():
    assert text_justify(["hello"], 8) == ['hello   ']

def test_uneven_gaps():
    assert text_justify(["a", "b", "c", "dd"], 6) == ['a  b c', 'dd    ']

def test_empty():
    assert text_justify([], 10) == []

def test_word_too_long():
    with pytest.raises(ValueError):
        text_justify(["abcdef"], 5)
