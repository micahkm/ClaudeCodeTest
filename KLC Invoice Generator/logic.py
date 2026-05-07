import re


def suggest_prefix(company_name: str) -> str:
    words = company_name.strip().split()
    if not words:
        return ""
    return words[0].upper()[:4]


def next_invoice_number(filenames: list[str], prefix: str) -> str:
    raise NotImplementedError
