from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StrategyRequest, StrategyResult
from app.services import lottery_service
from app.services.analysis_service import compute_stats
from app.services.strategy_service import recommend

router = APIRouter()


@router.post("/recommend", response_model=list[StrategyResult])
def get_recommendations(req: StrategyRequest, db: Session = Depends(get_db)):
    draws = lottery_service.get_all_draws(db)
    stats = compute_stats(draws)
    return recommend(stats, strategy=req.strategy, count=req.count)
