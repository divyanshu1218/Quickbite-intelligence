import os
from dotenv import load_dotenv


# Resolve project root dynamically
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

# Load local environment variables explicitly
load_dotenv(dotenv_path=ENV_PATH)

# Groq API settings (loaded from .env file or environment)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


# Database path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "qsr.duckdb")

# Development mode settings
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
