import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "FitBuddy - AI Fitness Plan Generator")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

    # Current Gemini model. You can change this in .env if needed.
    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/fitbuddy.db"
    )

    DEMO_MODE = not bool(GOOGLE_API_KEY)


settings = Settings()