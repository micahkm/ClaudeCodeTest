import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sheets import suggest_prefix, next_invoice_number


class TestSuggestPrefix:
    def test_single_word(self):
        assert suggest_prefix('Ukey') == 'UKEY'

    def test_first_word_only(self):
        assert suggest_prefix('Ukey Creation') == 'UKEY'

    def test_max_four_chars(self):
        assert suggest_prefix('Aloha Prints') == 'ALOH'

    def test_pewa(self):
        assert suggest_prefix('PEWA by Pono Potions') == 'PEWA'

    def test_empty_string(self):
        assert suggest_prefix('') == ''

    def test_three_char_word(self):
        assert suggest_prefix('KLC Hawaii') == 'KLC'


class TestNextInvoiceNumber:
    def test_increments_from_existing(self):
        titles = ['Invoice U013', 'Invoice U014', 'Invoice U015']
        assert next_invoice_number(titles, 'U') == 'U016'

    def test_starts_at_001_for_new_prefix(self):
        assert next_invoice_number([], 'X') == 'X001'

    def test_finds_max_not_last(self):
        titles = ['Invoice U015', 'Invoice U012', 'Invoice U009']
        assert next_invoice_number(titles, 'U') == 'U016'

    def test_multi_char_prefix(self):
        titles = ['Invoice PEWA001', 'Invoice PEWA002']
        assert next_invoice_number(titles, 'PEWA') == 'PEWA003'

    def test_ignores_other_prefixes(self):
        titles = ['Invoice U015', 'Invoice PEWA002']
        assert next_invoice_number(titles, 'U') == 'U016'

    def test_zero_pads_to_three_digits(self):
        assert next_invoice_number([], 'ABC') == 'ABC001'
