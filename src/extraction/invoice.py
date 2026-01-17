import re
from src.config import CURRENCY_REGEX

def extract_invoice(text: str) -> dict:

    result = {}

    # Invoice number
    inv_match = re.search(r"(INV[-_ ]?\d+)", text, re.IGNORECASE)
    result["invoice_number"] = inv_match.group(1) if inv_match else None

    # Date (YYYY-MM-DD or similar)
    date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", text)
    result["date"] = date_match.group(1) if date_match else None

    # Company (simplified: first capitalized word sequence)
    comp_match = re.search(r"Company[: ]+([A-Z][A-Za-z0-9 &]+)", text)
    result["company"] = comp_match.group(1) if comp_match else None

    # Total amount
    amt_match = re.search(r"Total[: ]+" + CURRENCY_REGEX, text)
    result["total_amount"] = amt_match.group(0) if amt_match else None

    return result
