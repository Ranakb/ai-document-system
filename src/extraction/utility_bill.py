import re
from src.config import CURRENCY_REGEX

def extract_utility_bill(text: str) -> dict:

    result = {}

    # Account number
    acct_match = re.search(r"(Account[-_ ]?\d+)", text, re.IGNORECASE)
    result["account_number"] = acct_match.group(1) if acct_match else None

    # Date
    date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", text)
    result["date"] = date_match.group(1) if date_match else None

    # Usage in kWh
    usage_match = re.search(r"(\d+(?:\.\d+)?)\s?kWh", text, re.IGNORECASE)
    result["usage_kwh"] = float(usage_match.group(1)) if usage_match else None

    # Amount due
    amt_match = re.search(r"Amount[: ]+" + CURRENCY_REGEX, text)
    result["amount_due"] = amt_match.group(0) if amt_match else None

    return result
