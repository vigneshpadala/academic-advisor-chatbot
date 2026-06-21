import os
from django.conf import settings
from .utils import extract_pdf_text
from .models import PDFDocument
from .vector_search import (
    is_vector_search_enabled,
    init_qdrant_client,
    ensure_collection,
    index_document,
)

PDF_DIR = os.path.join(settings.MEDIA_ROOT, "pdfs")


def load_all_pdfs():
    client = None
    if is_vector_search_enabled():
        client = init_qdrant_client()
        ensure_collection(client)

    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            path = os.path.join(PDF_DIR, file)
            try:
                text = extract_pdf_text(path)

                doc = PDFDocument.objects.create(
                    file_name=file,
                    content=text
                )
                print(f"✅ Loaded: {file}")

                if client is not None:
                    index_document(client, doc)

            except Exception as e:
                print(f"❌ Skipped (invalid PDF): {file}")
                print(f"   Reason: {e}")


