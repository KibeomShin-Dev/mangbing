from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import NumberStats, ReportData
from app.services import lottery_service
from app.services.analysis_service import compute_stats
from app.services.report_service import generate_report

router = APIRouter()


@router.get("/stats", response_model=list[NumberStats])
def number_stats(db: Session = Depends(get_db)):
    draws = lottery_service.get_all_draws(db)
    return compute_stats(draws)


@router.get("/report", response_model=ReportData)
def report(db: Session = Depends(get_db)):
    draws = lottery_service.get_all_draws(db)
    return generate_report(draws)
