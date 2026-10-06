import os
from dotenv import load_dotenv

load_dotenv("config/.env")

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "default")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:11434"
OLLAMA_MODEL = "llama3.1:8b"