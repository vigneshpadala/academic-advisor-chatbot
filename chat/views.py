from .models import PDFDocument
import re


# ================================
# 🔹 Helper functions
# ================================
def extract_cgpa(text):
    match = re.search(r"cgpa\s*([0-9.]+)", text.lower())
    return float(match.group(1)) if match else None


def extract_backlogs(text):
    match = re.search(r"backlogs?\s*([0-9]+)", text.lower())
    return int(match.group(1)) if match else 0


def extract_best_semester(text):
    sgpas = re.findall(r"sgpa\s*([0-9.]+)", text.lower())
    if not sgpas:
        return None, None

    sgpas_float = [float(s) for s in sgpas]
    max_sgpa = max(sgpas_float)
    sem_index = sgpas_float.index(max_sgpa)

    semester_map = {
        0: "1-1",
        1: "1-2",
        2: "2-1",
        3: "2-2"
    }

    return semester_map.get(sem_index), round(max_sgpa, 2)


def extract_external_marks_by_semester(text, semester):
    text = text.lower()
    pattern = rf"{semester}\s*results(.*?)(1-1\s*results|1-2\s*results|2-1\s*results|2-2\s*results|cgpa|sgpa|$)"
    match = re.search(pattern, text, re.DOTALL)

    if not match:
        return []

    block = match.group(1)

    return re.findall(
        r"([a-z &]+)\s+\d+\s+(\d+)\s+\d+\s+[a-z+o]+",
        block
    )


def format_table(headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def line():
        return "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    def row(row):
        return "|" + "|".join(f" {str(row[i]).ljust(col_widths[i])} " for i in range(len(row))) + "|"

    table = line() + "\n" + row(headers) + "\n" + line() + "\n"
    for r in rows:
        table += row(r) + "\n"
    return table + line()


def extract_student_summary(doc):
    sem, sgpa = extract_best_semester(doc.content)
    return {
        "cgpa": extract_cgpa(doc.content),
        "backlogs": extract_backlogs(doc.content),
        "best_semester": sem,
        "best_sgpa": sgpa,
    }


def get_topper_ranking(limit=5):
    student_map = {}
    for doc in PDFDocument.objects.all():
        cgpa = extract_cgpa(doc.content)
        if cgpa is None:
            continue
        student_no = doc.file_name.replace(".pdf", "")
        student_map[student_no] = max(student_map.get(student_no, 0), cgpa)

    return sorted(student_map.items(), key=lambda x: x[1], reverse=True)[:limit]


def get_semester_topper(semester):
    topper_student, topper_sgpa = None, -1.0
    pattern = rf"{semester}\s*results.*?sgpa\s*([0-9.]+)"

    for doc in PDFDocument.objects.all():
        match = re.search(pattern, doc.content.lower(), re.DOTALL)
        if match:
            sgpa = float(match.group(1))
            if sgpa > topper_sgpa:
                topper_sgpa = sgpa
                topper_student = doc.file_name.replace(".pdf", "")

    return (topper_student, round(topper_sgpa, 2)) if topper_student else (None, None)


# ================================
# 🔹 Chatbot main logic
# ================================
def chatbot_response(user_input):
    user_input = user_input.lower()

    # =====================================================
    # 🥇 SEMESTER-WISE TOPPER
    # =====================================================
    sem_match = re.search(r"(1-1|1-2|2-1|2-2)", user_input)
    if sem_match and "topper" in user_input:
        semester = sem_match.group(1)
        student_no, sgpa = get_semester_topper(semester)

        if not student_no:
            return f"❌ No SGPA data found for {semester} semester."

        return (
            f"🥇 Semester Topper – {semester}\n\n" +
            format_table(
                ["Rank", "Student", "SGPA"],
                [(1, f"Student {student_no}", sgpa)]
            )
        )

    # =====================================================
    # 🏆 TOPPER RANKING
    # =====================================================
    if re.search(r"topper|ranking|rank|top\s*\d*", user_input):
        limit = int(re.search(r"top\s*(\d+)", user_input).group(1)) if re.search(r"top\s*(\d+)", user_input) else 5
        toppers = get_topper_ranking(limit)

        return (
            "🏆 Topper Ranking (Based on CGPA)\n\n" +
            format_table(
                ["Rank", "Student", "CGPA"],
                [(i + 1, f"Student {s}", cgpa) for i, (s, cgpa) in enumerate(toppers)]
            )
        )

    # =====================================================
    # 🔹 STUDENT COMPARISON
    # =====================================================
    cmp = re.search(r"student\s*(\d+)\s*(vs|and)\s*student?\s*(\d+)", user_input)
    if cmp:
        d1 = PDFDocument.objects.filter(file_name=f"{cmp.group(1)}.pdf").first()
        d2 = PDFDocument.objects.filter(file_name=f"{cmp.group(3)}.pdf").first()
        if not d1 or not d2:
            return "❌ One or both student records not found."

        s1, s2 = extract_student_summary(d1), extract_student_summary(d2)
        return "📊 Student Comparison\n\n" + format_table(
            ["Metric", f"Student {cmp.group(1)}", f"Student {cmp.group(3)}"],
            [
                ("CGPA", s1["cgpa"], s2["cgpa"]),
                ("Backlogs", s1["backlogs"], s2["backlogs"]),
                ("Best Semester", s1["best_semester"], s2["best_semester"]),
                ("Best SGPA", s1["best_sgpa"], s2["best_sgpa"]),
            ]
        )

    # =====================================================
    # 🔹 SINGLE STUDENT FLOW
    # =====================================================
    sm = re.search(r"student\s*(\d+)|\b(\d+)\b", user_input)
    if not sm:
        return "❗ Please mention the student number (example: student 48 cgpa)."

    student_no = sm.group(1) or sm.group(2)
    doc = PDFDocument.objects.filter(file_name=f"{student_no}.pdf").first()
    if not doc:
        return f"❌ Student {student_no} record not found."

    # Semester external marks
    if sem_match and ("external" in user_input or "marks" in user_input):
        rows = extract_external_marks_by_semester(doc.content, sem_match.group(1))
        if not rows:
            return f"❌ External marks not found for {sem_match.group(1)} semester."

        return (
            f"📘 Student {student_no} – {sem_match.group(1)} Semester External Marks\n\n" +
            format_table(
                ["Subject", "External Marks"],
                [(s.title(), m) for s, m in rows]
            )
        )

    if "cgpa" in user_input:
        return f"📘 Student {student_no} CGPA is {extract_cgpa(doc.content)}"

    if "backlog" in user_input:
        return f"📘 Student {student_no} has {extract_backlogs(doc.content)} backlogs."

    if "best semester" in user_input:
        sem, sgpa = extract_best_semester(doc.content)
        return f"📘 Student {student_no}'s best semester is {sem} with SGPA {sgpa}."

    return (
        f"❗ What information do you want about Student {student_no}?\n"
        f"You can ask: CGPA, backlogs, best semester, semester external marks, "
        f"comparison, topper ranking."
    )







# ✔ Semester-wise topper
# ✔ Overall topper ranking
# ✔ Student comparison
# ✔ Semester external marks (table)
# ✔ CGPA / backlogs / best semester
# ✔ No runtime errors

    