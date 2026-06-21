from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


ENV_TEMPLATE = """# Generated environment bootstrap file for chatbot_project

# General provider selection: openai or gemini
LLM_PROVIDER=openai

# OpenAI configuration
OPENAI_API_KEY=
OPENAI_CHAT_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Gemini configuration
GOOGLE_API_KEY=
GEMINI_CHAT_MODEL=gemini-1.5-pro

# Qdrant vector search configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=student_data

# ElevenLabs voice configuration
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_NAME=alloy
ELEVENLABS_MODEL=eleven_multilingual_v1

# Optional runtime flags
# DEBUG=True
"""


class Command(BaseCommand):
    help = "Bootstraps model and environment configuration files for the chatbot project."

    def add_arguments(self, parser):
        parser.add_argument(
            "--example",
            action="store_true",
            help="Create or update .env.example with the recommended variables.",
        )
        parser.add_argument(
            "--env",
            action="store_true",
            help="Create .env from the example if it does not already exist.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing .env.example and .env files if they already exist.",
        )

    def handle(self, *args, **options):
        project_root = Path(settings.BASE_DIR)
        env_example_path = project_root / ".env.example"
        env_path = project_root / ".env"
        created_any = False

        if options["example"] or not (options["env"] or options["force"]):
            if env_example_path.exists() and not options["force"]:
                self.stdout.write(self.style.NOTICE(f".env.example already exists at {env_example_path}. Use --force to overwrite."))
            else:
                env_example_path.write_text(ENV_TEMPLATE)
                self.stdout.write(self.style.SUCCESS(f"Created .env.example at {env_example_path}."))
                created_any = True

        if options["env"]:
            if env_path.exists() and not options["force"]:
                self.stdout.write(self.style.NOTICE(f".env already exists at {env_path}. Use --force to overwrite."))
            else:
                if not env_example_path.exists():
                    env_example_path.write_text(ENV_TEMPLATE)
                    self.stdout.write(self.style.SUCCESS(f"Created .env.example at {env_example_path}."))
                env_path.write_text(ENV_TEMPLATE)
                self.stdout.write(self.style.SUCCESS(f"Created .env at {env_path}."))
                created_any = True

        if not options["example"] and not options["env"] and not created_any:
            self.stdout.write(self.style.WARNING(
                "No files were created. Use --example to generate .env.example or --env to generate .env."
            ))
            self.stdout.write(
                "Example: python manage.py bootstrap_model_config --example --env"
            )
