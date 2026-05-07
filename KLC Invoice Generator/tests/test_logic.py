import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from logic import suggest_prefix, next_invoice_number


class TestSuggestPrefix:
    def test_single_word_truncates_to_four(self):
        assert suggest_prefix("Umauma") == "UMAU"

    def test_multi_word_uses_first_word(self):
        assert suggest_prefix("Koolau Laser Creations") == "KOOL"

    def test_short_name_no_padding(self):
        assert suggest_prefix("AB") == "AB"

    def test_empty_string_returns_empty(self):
        assert suggest_prefix("") == ""

    def test_already_uppercase(self):
        assert suggest_prefix("ACME Corp") == "ACME"

    def test_leading_whitespace_stripped(self):
        assert suggest_prefix("  Umauma") == "UMAU"

    def test_exactly_four_chars(self):
        assert suggest_prefix("ABCD Extra") == "ABCD"
