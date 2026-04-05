import re

def extract_section(header, text):
    pattern = rf"(?:\d+\.\s*)?{header}[:\s]*(.*?)(?=\n\s*(?:\d+\.)?\s*[A-Z_ ]+:|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


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

Evaluation Breakdown:

Education Assessment:
- The applicant's Bachelor's Degree in Computer Science matches the visa requirements.

Employment Assessment:
- Not explicitly detailed here.

Income Assessment:
- Meets criteria.

Policy Match:
- Good.

Risk Factors:
- None

Actionable Suggestions:
- None

Required Documents:
- Standard documents required

Final Assessment:
- Seems fine.
"""

with open("test_out.txt", "w", encoding="utf-8") as f:
    f.write(repr(extract_section("Evaluation Breakdown", text)))
