import re

def extract_section(header, text):
    pattern = rf"(?:\d+\.\s*)?{header}[:\s]*(.*?)(?=\n\s*(?:\d+\.)?\s*[A-Z_ ]+:|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_list(header, text):
    block = extract_section(header, text)
    if block:
        # Strip out long dashed lines before matching to prevent artifacts
        block = re.sub(r"-{4,}", "", block)
        items = re.findall(r"(?:-|\•|\d+\.)\s*(.+)", block)
        if not items:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            return [l for l in lines if l.lower() != "none"]
        return [i.strip() for i in items if i.strip().lower() != "none" and i.strip().lower() != ""]
    return []

def extract_subfield(section_text, field_name):
    # Matches either "- FieldName: ..." or "FieldName:\n- ..."
    # Strip long dashed lines first
    section_text = re.sub(r"-{4,}", "", section_text)
    pattern = rf"(?:-\s*)?{field_name}[:\s]+(.*?)(?=\n(?:-\s*)?[A-Za-z ]+[:\s]|$)"
    match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        if val.startswith('-'):
            val = val[1:].strip()
        return val
    return "Not explicitly detailed."

text = """
Decision: Eligible

Confidence: 0.9

Key Findings:
- point 1
- point 2

Requirements Met:
- req 1

Requirements Not Met:
- req 2

----------------------------------------

Evaluation Breakdown:

Education Assessment:
- The applicant's Bachelor's Degree in Computer Science matches the visa requirements.

Employment Assessment:
- Not explicitly detailed here.

Income Assessment:
- Meets criteria.

Policy Match:
- Good.

----------------------------------------

Risk Factors:
- None

Actionable Suggestions:
- None

Required Documents:
- Standard documents required

----------------------------------------

Final Assessment:
- Seems fine.
"""

print("Req Met:", extract_list("Requirements Met", text))
print("Req Not Met:", extract_list("Requirements Not Met", text))
print("Edu:", extract_subfield(text, "Education Assessment"))
print("Emp:", extract_subfield(text, "Employment Assessment"))
print("Pol:", extract_subfield(text, "Policy Match"))
