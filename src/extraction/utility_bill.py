import re
from src.config import CURRENCY_REGEX

def extract_utility_bill(text: str) -> dict:

    result = {}

    # Account number - flexible patterns: Account Number: ACC-49575, Account: ACC-123, etc.
    acct_patterns = [
        r"[Aa]ccount\s+[Nn]umber[: ]+([A-Z0-9-]+)",  # Account Number: ACC-49575
        r"[Aa]ccount[: ]+([A-Z0-9-]+)",  # Account: ACC-123
        r"[Aa]ccount\s+#?([A-Z0-9-]+)",  # Account #ACC-49575
    ]
    acct_match = None
    for pattern in acct_patterns:
        acct_match = re.search(pattern, text)
        if acct_match:
            result["account_number"] = acct_match.group(1)
            break
    if not acct_match:
        result["account_number"] = None

    # Date - handle various date formats
    date_patterns = [
        r"[Bb]illing\s+[Dd]ate[: ]+(\d{4}[-/]\d{2}[-/]\d{2})",  # Billing Date: 2025-05-24
        r"[Dd]ate[: ]+(\d{4}[-/]\d{2}[-/]\d{2})",  # Date: 2025-05-24
        r"(\d{4}[-/]\d{2}[-/]\d{2})",  # General YYYY-MM-DD format
    ]
    date_match = None
    for pattern in date_patterns:
        date_match = re.search(pattern, text)
        if date_match:
            result["date"] = date_match.group(1)
            break
    if not date_match:
        result["date"] = None

    # Usage in kWh - look for number followed by kWh
    usage_match = re.search(r"[Uu]sage[: ]+(\d+(?:\.\d+)?)\s*[Kk][Ww][Hh]", text)
    if not usage_match:
        usage_match = re.search(r"(\d+(?:\.\d+)?)\s*[Kk][Ww][Hh]", text)
    result["usage_kwh"] = float(usage_match.group(1)) if usage_match else None

    # Amount due - flexible patterns for "Amount Due:", "Amount:", "Total Due:"
    amt_patterns = [
        r"[Aa]mount\s+[Dd]ue[: ]+(\$?[\d,]+\.?\d*)",  # Amount Due: $193.00
        r"[Aa]mount[: ]+(\$?[\d,]+\.?\d*)",  # Amount: $193.00
        r"[Tt]otal\s+[Dd]ue[: ]+(\$?[\d,]+\.?\d*)",  # Total Due: $193.00
    ]
    amt_match = None
    for pattern in amt_patterns:
        amt_match = re.search(pattern, text)
        if amt_match:
            result["amount_due"] = amt_match.group(1)
            break
    if not amt_match:
        result["amount_due"] = None

    return result
