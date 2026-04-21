from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import NumberStats
from app.services import lottery_service
from app.services.analysis_service import compute_stats

router = APIRouter()


@router.get("/stats", response_model=list[NumberStats])
def number_stats(db: Session = Depends(get_db)):
    draws = lottery_service.get_all_draws(db)
    return compute_stats(draws)
