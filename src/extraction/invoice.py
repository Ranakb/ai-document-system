import re
from src.config import CURRENCY_REGEX

def extract_invoice(text: str) -> dict:

    result = {}

    # Invoice number - flexible patterns: INV-1234, Invoice #1001, Invoice: 1001, etc.
    inv_patterns = [
        r"Invoice\s*[#:]?\s*(\d+)",  # Invoice #1001 or Invoice: 1001
        r"(INV[-_ ]?\d+)",  # INV-1001
        r"[Ii]nvoice\s+[Nn]umber[: ]+([A-Z0-9-]+)",  # Invoice Number: INV-123
    ]
    inv_match = None
    for pattern in inv_patterns:
        inv_match = re.search(pattern, text, re.IGNORECASE)
        if inv_match:
            result["invoice_number"] = inv_match.group(1) if inv_match.lastindex else inv_match.group(0)
            break
    if not inv_match:
        result["invoice_number"] = None

    # Date (YYYY-MM-DD or similar)
    date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", text)
    result["date"] = date_match.group(1) if date_match else None

    # Company - look for "Company:" or company name after key terms
    comp_patterns = [
        r"[Cc]ompany[: ]+([A-Z][A-Za-z0-9 &.,'-]*?)(?:\n|$)",  # Company: Pioneer Ltd
        r"[Ff]rom[: ]+([A-Z][A-Za-z0-9 &.,'-]*?)(?:\n|$)",  # From: Company Name
    ]
    comp_match = None
    for pattern in comp_patterns:
        comp_match = re.search(pattern, text)
        if comp_match:
            result["company"] = comp_match.group(1).strip()
            break
    if not comp_match:
        result["company"] = None

    # Total amount - flexible: "Total:", "Total Amount:", "Grand Total:"
    amt_patterns = [
        r"[Tt]otal\s+[Aa]mount[: ]+(\$?[\d,]+\.?\d*)",  # Total Amount: $2073.00
        r"[Tt]otal[: ]+(\$?[\d,]+\.?\d*)",  # Total: $2073.00
        r"[Gg]rand\s+[Tt]otal[: ]+(\$?[\d,]+\.?\d*)",  # Grand Total: $2073.00
    ]
    amt_match = None
    for pattern in amt_patterns:
        amt_match = re.search(pattern, text)
        if amt_match:
            result["total_amount"] = amt_match.group(1)
            break
    if not amt_match:
        result["total_amount"] = None

    return result
