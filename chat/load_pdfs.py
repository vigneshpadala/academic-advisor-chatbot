import os
from django.conf import settings
from .utils import extract_pdf_text
from .models import PDFDocument

PDF_DIR = os.path.join(settings.MEDIA_ROOT, "pdfs")

def load_all_pdfs():
    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            path = os.path.join(PDF_DIR, file)
            try:
                text = extract_pdf_text(path)

                PDFDocument.objects.create(
                    file_name=file,
                    content=text
                )
                print(f"✅ Loaded: {file}")

            except Exception as e:
                print(f"❌ Skipped (invalid PDF): {file}")
                print(f"   Reason: {e}")


