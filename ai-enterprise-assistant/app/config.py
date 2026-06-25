import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini-2.5-flash-lite")
LLM_TIMEOUT_SECONDS = int(os.environ.get("LLM_TIMEOUT_SECONDS", "20"))
