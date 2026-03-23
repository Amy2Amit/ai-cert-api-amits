import re


def parse_acord_data(text):
    data = {}

    # Vendor / Named Insured
    vendor = re.search(r"(Named Insured|Vendor)[:\s]+(.+)", text, re.IGNORECASE)

    # Policy Number
    policy = re.search(r"Policy\s*Number[:\s]+(\S+)", text, re.IGNORECASE)

    # Coverage Type
    coverage = re.search(r"General Liability", text, re.IGNORECASE)

    # Limits (basic example)
    limit = re.search(r"Each Occurrence[:\s\$]+([\d,]+)", text, re.IGNORECASE)

    data["vendor"] = vendor.group(2).strip() if vendor else None
    data["policy_number"] = policy.group(1) if policy else None
    data["coverage"] = "General Liability" if coverage else None
    data["limit"] = int(limit.group(1).replace(",", "")) if limit else 0

    return data