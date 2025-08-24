import pytest
from app.calculator import Calculator

class TestСalc:
    def setup_method(self):
        self.calc= Calculator()

    def test_adding_success(self):
        assert self.calc.adding(1, 1) == 2

    def test_multiply_calculate_correctly(self):
        assert self.calc.multiply(2, 2) == 4


    def test_multiply_failed(self):
        assert self.calc.multiply(2, 2) == 5