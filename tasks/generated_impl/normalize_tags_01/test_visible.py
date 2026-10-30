import pytest
from normalize_tags import normalize_tags

def test_sorted():
    assert normalize_tags(["python", "api", "Testing"]) == ['api', 'python', 'Testing']

def test_duplicates():
    assert normalize_tags(["Python", "python", "PYTHON"]) == ['Python']

def test_trim_and_drop_empty():
    assert normalize_tags(["  web ", "", "   ", "Web"]) == ['web']

def test_keeps_first_spelling():
    assert normalize_tags(["DevOps", "b", "devops"]) == ['b', 'DevOps']

def test_not_a_list():
    with pytest.raises(TypeError):
        normalize_tags("python")
