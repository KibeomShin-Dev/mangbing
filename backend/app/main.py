import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine
from app.models import Base
from app.routers import lottery, analysis, strategy

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mangbing API", version="1.0.0")

# 로컬 개발 + 프로덕션 프론트엔드 URL 모두 허용
# FRONTEND_URL 환경변수로 Vercel 배포 URL 추가
_origins = ["http://localhost:5173"]
if os.getenv("FRONTEND_URL"):
    _origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lottery.router, prefix="/api/lottery", tags=["lottery"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(strategy.router, prefix="/api/strategy", tags=["strategy"])


@app.get("/")
def root():
    return {"message": "Mangbing API"}
