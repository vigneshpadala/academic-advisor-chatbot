import json
import re

from .models import PDFDocument
from .tts import generate_speech, is_tts_enabled
from .vector_search import (
    is_vector_search_enabled,
    qdrant_search,
    generate_ai_response,
)
from django.shortcuts import render
from django.http import HttpResponse


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


def extract_student_profile(text):
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    def find(pattern, group=0):
        """
        group=0 → full match
        group=1 → first capturing group
        """
        m = re.search(pattern, text, re.IGNORECASE)
        if not m:
            return "Not available"
        return m.group(group).strip()

    # -------------------------------
    # NAME (ignore headings like ACADEMIC RESULTS)
    # -------------------------------
    name = "Not available"
    for match in re.findall(r"\b[A-Z]{3,}(?:\s+[A-Z]{3,}){1,3}\b", text):
        if match not in ["ACADEMIC RESULTS", "SUBJECT NAME", "COLLEGE NAME"]:
            name = match
            break

    profile = {
        # 👤 Basic Info
        "name": name,

        # Roll number → NO capturing group → group=0
        "rollno": find(r"\b\d{2,}[A-Z0-9]{4,}\b", 0),

        "branch": find(
            r"(CSE\s*\(.*?\)|COMPUTER\s*SCIENCE.*?ENGINEERING.*?)", 1
        ),

        "college": find(
            r"(KASIREDDY\s*NARAYAN\s*REDDY\s*COLLEGE.*?RESEARCH)", 1
        ),
    }

    return profile



# ================================
# 🔹 Chatbot main logic
# ================================
def chatbot_response(user_input):
    user_input = user_input.lower().strip()

    # =====================================================
    # 👋 GREETING
    # =====================================================
    if re.fullmatch(r"(hi|hello|hey|hai|hii)", user_input):
        return (
        "👋 Hello! Welcome to the Student Academic Assistant😊\n\n"
        "I can help you explore student profiles, CGPA, semester toppers, comparisons, and academic insights.\n\n"
        "Try:\n"
        "• Student rollno → full profile \n"
        "• Student rollno CGPA\n"
        "• Student rollno backlogs\n"
        "• Student rollno best semester\n"
        "• Student rollno vs Student rollno comparison\n"
        "• Top 10 students\n"
        "• 1-1 semester topper\n\n"
    )

    # =====================================================
    # 🥇 SEMESTER TOPPER (FIRST)
    # =====================================================
    sem_match = re.search(r"(1-1|1-2|2-1|2-2)", user_input)
    if sem_match and "topper" in user_input:
        semester = sem_match.group(1)
        student_no, sgpa = get_semester_topper(semester)

        if not student_no:
            return f"❌ No topper data found for {semester} semester."

        return (
            f"🥇 Semester Topper – {semester}\n\n"
            + format_table(
                ["Rank", "Student", "SGPA"],
                [(1, f"Student {student_no}", sgpa)]
            )
        )

    # =====================================================
    # 🏆 OVERALL TOPPER RANKING
    # =====================================================
    if re.search(r"topper|ranking|rank|top\s*\d*", user_input):
        limit_match = re.search(r"top\s*(\d+)", user_input)
        limit = int(limit_match.group(1)) if limit_match else 5

        toppers = get_topper_ranking(limit)
        if not toppers:
            return "❌ No CGPA data available."

        return (
            "🏆 Topper Ranking (Based on CGPA)\n\n"
            + format_table(
                ["Rank", "Student", "CGPA"],
                [(i + 1, f"Student {s}", cgpa) for i, (s, cgpa) in enumerate(toppers)]
            )
        )

    # =====================================================
    # 📊 STUDENT COMPARISON
    # =====================================================
    cmp = re.search(r"student\s*(\d+)\s*(vs|and)\s*student?\s*(\d+)", user_input)
    if cmp:
        s1, s2 = cmp.group(1), cmp.group(3)

        d1 = PDFDocument.objects.filter(file_name=f"{s1}.pdf").first()
        d2 = PDFDocument.objects.filter(file_name=f"{s2}.pdf").first()

        if not d1 or not d2:
            return "❌ One or both student records not found."

        s1_data = extract_student_summary(d1)
        s2_data = extract_student_summary(d2)

        return (
            "📊 Student Comparison\n\n"
            + format_table(
                ["Metric", f"Student {s1}", f"Student {s2}"],
                [
                    ("CGPA", s1_data["cgpa"], s2_data["cgpa"]),
                    ("Backlogs", s1_data["backlogs"], s2_data["backlogs"]),
                    ("Best Semester", s1_data["best_semester"], s2_data["best_semester"]),
                    ("Best SGPA", s1_data["best_sgpa"], s2_data["best_sgpa"]),
                ]
            )
        )

    # =====================================================
    # 👤 SINGLE STUDENT (LAST)
    # =====================================================
    sm = re.search(r"(?:student\s*)?(\d+)", user_input)
    if sm:
        student_no = sm.group(1)
        doc = PDFDocument.objects.filter(file_name=f"{student_no}.pdf").first()

        if not doc:
            return f"❌ Student {student_no} record not found."

        # CGPA only
        if "cgpa" in user_input:
            cgpa = extract_cgpa(doc.content)
            return f"📊 Student {student_no} CGPA: {cgpa if cgpa else 'N/A'}"

        # Backlogs
        if "backlog" in user_input:
            return f"📘 Student {student_no} Backlogs: {extract_backlogs(doc.content)}"

        # Best semester
        if "best semester" in user_input:
            sem, sgpa = extract_best_semester(doc.content)
            return f"📘 Best Semester: {sem}, SGPA: {sgpa}"

        # FULL PROFILE (only when user says just number)
        if re.fullmatch(r"(student\s*)?\d+", user_input):
            profile = extract_student_profile(doc.content)
            summary = extract_student_summary(doc)

            return (
    "👤 Student Profile\n\n"
    f"Name         : {profile.get('name')}\n"
    f"Roll No      : {profile.get('rollno')}\n"
    f"Branch       : {profile.get('branch')}\n"
    f"College      : {profile.get('college')}\n\n"
    "📊 Academic Summary\n"
    f"CGPA         : {summary['cgpa']}\n"
    f"Backlogs     : {summary['backlogs']}\n"
    f"Best Sem     : {summary['best_semester']}\n"
    f"Best SGPA    : {summary['best_sgpa']}"
)


# =====================================================
# 🤖 FALLBACK (SMART HELP MESSAGE)
# =====================================================

    if is_vector_search_enabled():
        hits = qdrant_search(user_input, top_k=5)
        if hits:
            return generate_ai_response(user_input, hits)

    return (
    "🤖 I can help with student academic details.\n\n"
    "You can ask things like:\n"
    "• Student → full profile\n"
    "• Student CGPA\n"
    "• Student backlogs\n"
    "• Student best semester\n"
    "• Student  vs Student comparison\n"
    "• Top 10 students\n"
    "• 1-1 semester topper\n\n"
    "📌 Tip: Just type the student number to see full details."
)








def chat_view(request):
    if request.method == "POST":
        user_msg = request.POST.get("message", "")
        response = chatbot_response(user_msg)
        return HttpResponse(response)

    return render(request, "chat.html")


def speak_view(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    if not is_tts_enabled():
        return HttpResponse("TTS is not configured.", status=501)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        message = payload.get("message", "")
    except Exception:
        return HttpResponse("Invalid JSON payload.", status=400)

    if not message:
        return HttpResponse("Missing message to speak.", status=400)

    try:
        audio_bytes = generate_speech(message)
        return HttpResponse(audio_bytes, content_type="audio/mpeg")
    except Exception as exc:
        return HttpResponse(str(exc), status=500)





# ✔ Semester-wise topper
# ✔ Overall topper ranking
# ✔ Student comparison
# ✔ Semester external marks (table)
# ✔ CGPA / backlogs / best semester
# ✔ No runtime errors

    