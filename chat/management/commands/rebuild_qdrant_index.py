from django.core.management.base import BaseCommand

from chat.vector_search import is_vector_search_enabled, index_all_documents


class Command(BaseCommand):
    help = "Rebuilds the Qdrant index for all stored PDF student documents."

    def handle(self, *args, **options):
        if not is_vector_search_enabled():
            self.stderr.write(self.style.ERROR(
                "Qdrant vector search is not enabled. Ensure QDRANT_URL and OPENAI_API_KEY are configured."
            ))
            return

        self.stdout.write(self.style.NOTICE("Starting Qdrant index rebuild for all PDFs..."))
        try:
            index_all_documents()
            self.stdout.write(self.style.SUCCESS("✅ Qdrant index rebuild completed successfully."))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"❌ Failed to rebuild Qdrant index: {exc}"))
