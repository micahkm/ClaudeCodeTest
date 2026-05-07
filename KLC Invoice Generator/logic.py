import re


def suggest_prefix(company_name: str) -> str:
    words = company_name.strip().split()
    if not words:
        return ""
    return words[0].upper()[:4]


def next_invoice_number(filenames: list[str], prefix: str) -> str:
    pattern = re.compile(
        rf'^Invoice {re.escape(prefix)}(\d+)$', re.IGNORECASE
    )
    numbers = []
    for name in filenames:
        m = pattern.match(name.strip())
        if m:
            numbers.append(int(m.group(1)))
    next_num = (max(numbers) + 1) if numbers else 1
    return f"{prefix}{next_num:03d}"
