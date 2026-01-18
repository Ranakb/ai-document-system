import re
from src.config import EMAIL_REGEX, PHONE_REGEX

def extract_resume(text: str) -> dict:

    result = {}

    lines = text.split("\n")
    # Name: assume first non-empty line
    result["name"] = lines[0] if lines else None

    # Email
    email_match = re.search(EMAIL_REGEX, text)
    result["email"] = email_match.group(0) if email_match else None

    # Phone
    phone_match = re.search(PHONE_REGEX, text)
    if phone_match:
        phone = phone_match.group(0).strip()
        # Remove any newlines or carriage returns
        phone = phone.replace('\n', '').replace('\r', '').strip()
        result["phone"] = phone
    else:
        result["phone"] = None

    # Experience: simple heuristic
    exp_match = re.search(r"(\d+)\s+years?", text, re.IGNORECASE)
    result["experience_years"] = int(exp_match.group(1)) if exp_match else None

    return result
