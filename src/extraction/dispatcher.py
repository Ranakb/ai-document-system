from .invoice import extract_invoice
from .resume import extract_resume
from .utility_bill import extract_utility_bill

def extract_fields(doc_class: str, text: str) -> dict:
    """
    Dispatch extraction based on document class.
    Returns an empty dict for Other / Unclassifiable.
    """
    if doc_class == "Invoice":
        return extract_invoice(text)
    elif doc_class == "Resume":
        return extract_resume(text)
    elif doc_class == "Utility Bill":
        return extract_utility_bill(text)
    else:
        return {}
