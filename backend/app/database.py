from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()

# DATABASE_URL 환경변수 우선 (Neon PostgreSQL 등 프로덕션 DB)
# 없으면 로컬 SQLite로 폴백
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Neon/Render가 제공하는 URL이 postgres:// 형식일 경우 수정
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "lotto.db"))
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
