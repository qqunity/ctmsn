from __future__ import annotations

import os


SECRET_KEY: str = os.environ.get("CTMSN_SECRET_KEY", "dev-secret-change-in-production")
DATABASE_URL: str = os.environ.get("CTMSN_DATABASE_URL", "sqlite:///ctmsn.db")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("CTMSN_ACCESS_TOKEN_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get("CTMSN_REFRESH_TOKEN_DAYS", "7"))
ALGORITHM: str = "HS256"
CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.environ.get("CTMSN_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if o.strip()
]
