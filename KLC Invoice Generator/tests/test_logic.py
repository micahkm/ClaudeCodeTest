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


class TestNextInvoiceNumber:
    def test_no_prior_invoices_starts_at_001(self):
        assert next_invoice_number([], "U") == "U001"

    def test_single_prior_invoice_increments(self):
        assert next_invoice_number(["Invoice U015"], "U") == "U016"

    def test_multiple_picks_max(self):
        files = ["Invoice U010", "Invoice U015", "Invoice U012"]
        assert next_invoice_number(files, "U") == "U016"

    def test_ignores_other_prefixes(self):
        files = ["Invoice U015", "Invoice K003"]
        assert next_invoice_number(files, "U") == "U016"

    def test_case_insensitive_match(self):
        assert next_invoice_number(["invoice u015"], "U") == "U016"

    def test_pads_to_three_digits(self):
        assert next_invoice_number(["Invoice U099"], "U") == "U100"

    def test_prefix_in_number_part_not_matched(self):
        # "Invoice UA001" should not match prefix "U"
        assert next_invoice_number(["Invoice UA001"], "U") == "U001"

    def test_four_char_prefix(self):
        assert next_invoice_number(["Invoice KOOL003"], "KOOL") == "KOOL004"
