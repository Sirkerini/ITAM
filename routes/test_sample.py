import pytest

# test_math.py

def add(x, y):
    return x + y

def test_add_success():
    assert add(2, 3) == 5

def test_add_failure():
    assert add(2, 4) == 6  # This test will intentionally fail
