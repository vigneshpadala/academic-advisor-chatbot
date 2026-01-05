# chat/utils.py

import re
import pdfplumber

# =====================================
# 📄 PDF TEXT EXTRACTION
# =====================================
def extract_pdf_text(pdf_path):
    """
    Extracts full text from a PDF file
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# =====================================
# 👤 STUDENT PROFILE EXTRACTION
# =====================================
def extract_student_profile(text):
    """
    Extract student personal + academic details from PDF text
    """
    text = text.replace("\n", " ")

    # Name, Roll No, College Code, Father Name
    profile_match = re.search(
        r"([A-Z ]+)\s+(\d{10})\s+(\d+[A-Z])\s+([A-Z ]+)",
        text
    )

    name = profile_match.group(1).title() if profile_match else "Not available"
    rollno = profile_match.group(2) if profile_match else "Not available"
    college_code = profile_match.group(3) if profile_match else "Not available"
    father_name = profile_match.group(4).title() if profile_match else "Not available"

    # College & Branch
    college_match = re.search(
        r"(KASIREDDY NARAYAN REDDY COLLEGE OF ENGINEERING & RESEARCH)",
        text
    )
    branch_match = re.search(
        r"(CSE\s*\(.*?\)|CSE|ECE|EEE|MECH|CIVIL)",
        text
    )

    college = college_match.group(1) if college_match else "Not available"
    branch = branch_match.group(1) if branch_match else "Not available"

    return {
        "name": name,
        "rollno": rollno,
        "college_code": college_code,
        "father_name": father_name,
        "college": college,
        "branch": branch
    }


# =====================================
# 📊 CGPA EXTRACTION
# =====================================
def extract_cgpa(text):
    match = re.search(r"cgpa\s*[:\-]?\s*([0-9.]+)", text.lower())
    return float(match.group(1)) if match else None


# =====================================
# ❌ BACKLOG EXTRACTION
# =====================================
def extract_backlogs(text):
    match = re.search(r"backlogs?\s*[:\-]?\s*(\d+)", text.lower())
    return int(match.group(1)) if match else 0


# =====================================
# 🥇 BEST SEMESTER
# =====================================
def extract_best_semester(text):
    sgpas = re.findall(r"sgpa\s*[:\-]?\s*([0-9.]+)", text.lower())
    if not sgpas:
        return None, None

    sgpas = [float(s) for s in sgpas]
    best_sgpa = max(sgpas)
    index = sgpas.index(best_sgpa)

    semester_map = {
        0: "1-1",
        1: "1-2",
        2: "2-1",
        3: "2-2"
    }

    return semester_map.get(index), best_sgpa


# =====================================
# 📘 FULL STUDENT SUMMARY
# =====================================
def extract_student_summary(text):
    sem, sgpa = extract_best_semester(text)
    return {
        "cgpa": extract_cgpa(text),
        "backlogs": extract_backlogs(text),
        "best_semester": sem,
        "best_sgpa": sgpa
    }

