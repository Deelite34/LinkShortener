import string

from django.test import TestCase

from ..utils.utils import random_sequence


class TestUtils(TestCase):
    """
    Tests utility functions from utils.py file
    """
    def test_random_sequence(self):
        length = 10
        test_sequence = random_sequence(length)
        uses_correct_signs = True

        for letter in test_sequence:
            if letter not in string.ascii_letters:
                uses_correct_signs = False
                break
        has_correct_length = len(test_sequence) == length

        self.assertTrue(uses_correct_signs)
        self.assertTrue(has_correct_length)
