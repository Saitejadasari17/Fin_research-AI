import os

class Settings:
    PROJECT_NAME: str = "FinResearch AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Provider keys (optional - fallback mock engines included for reliable offline execution)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    
    # Financial engine defaults
    DEFAULT_RISK_FREE_RATE: float = 0.042  # 4.2% US 10Y Yield
    DEFAULT_EQUITY_RISK_PREMIUM: float = 0.055 # 5.5% ERP
    DEFAULT_MONTE_CARLO_RUNS: int = 5000

settings = Settings()
