import os

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/app.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    AI_PROVIDER_URL = os.getenv("AI_PROVIDER_URL", "http://localhost:8000/ai")
    # Adicione outras configurações aqui conforme necessário


