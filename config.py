import os
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False
from i18n import Language

load_dotenv()

class Config:
    # Azure settings
    AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "")
    AZURE_PROJECT_NAME = os.getenv("AZURE_PROJECT_NAME", "studymate-ai")
    AZURE_REGION = os.getenv("AZURE_REGION", "eastus")

    # Microsoft Foundry IQ — Primary intelligence layer
    FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY", "")
    FOUNDRY_ENDPOINT = os.getenv(
        "FOUNDRY_ENDPOINT",
        "https://studymate-ai-resource.services.ai.azure.com/api/projects/studymate-ai",
    )
    FOUNDRY_MODEL = os.getenv("FOUNDRY_MODEL", "gpt-4o")

    # Azure OpenAI — Model backbone via Foundry
    AZURE_OPENAI_ENDPOINT = os.getenv(
        "AZURE_OPENAI_ENDPOINT",
        "https://studymate-ai-resource.openai.azure.com",
    )
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    # Groq — Emergency fallback only if Azure is unavailable
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4.1-mini")

    # App settings
    APP_NAME = "StudyMate AI"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # Multi-language settings
    DEFAULT_LANGUAGE = Language.__members__.get(
        os.getenv("DEFAULT_LANGUAGE", "ENGLISH").upper(),
        Language.ENGLISH,
    )
    SUPPORTED_LANGUAGES = [Language.ENGLISH, Language.HINDI, Language.TAMIL, Language.KANNADA]

    # Agent thresholds
    WEAK_SUBJECT_THRESHOLD = 60.0
    MODERATE_SUBJECT_THRESHOLD = 75.0
    HIGH_RISK_THRESHOLD = 70.0
    CRITICAL_RISK_THRESHOLD = 85.0

    # Study plan settings
    MIN_STUDY_HOURS_PER_DAY = 2
    MAX_STUDY_HOURS_PER_DAY = 8
    SUBJECTS_PER_DAY = 3

config = Config()
