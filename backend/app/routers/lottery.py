import os
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LottoDraw, DBStatus
from app.services import lottery_service
from app.services.update_service import run_update

router = APIRouter()


@router.get("/status", response_model=DBStatus)
def db_status(db: Session = Depends(get_db)):
    status = lottery_service.get_db_status(db)
    if not status:
        raise HTTPException(status_code=404, detail="DB에 데이터가 없습니다.")
    return status


@router.get("/", response_model=list[LottoDraw])
def list_draws(limit: int = 100, db: Session = Depends(get_db)):
    return lottery_service.get_recent_draws(db, n=limit)


@router.get("/all", response_model=list[LottoDraw])
def all_draws(db: Session = Depends(get_db)):
    return lottery_service.get_all_draws(db)


@router.get("/{round_no}", response_model=LottoDraw)
def get_draw(round_no: int, db: Session = Depends(get_db)):
    draw = lottery_service.get_draw(db, round_no)
    if not draw:
        raise HTTPException(status_code=404, detail=f"{round_no}회차 데이터가 없습니다.")
    return draw


@router.post("/update")
def update_db(
    x_update_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """신규 회차를 동행복권 API에서 가져와 DB에 저장.
    UPDATE_TOKEN 환경변수가 설정된 경우 X-Update-Token 헤더로 인증 필요."""
    expected_token = os.getenv("UPDATE_TOKEN")
    if expected_token and x_update_token != expected_token:
        raise HTTPException(status_code=401, detail="인증 토큰이 올바르지 않습니다.")

    result = run_update(db)
    if result.error:
        raise HTTPException(status_code=500, detail=result.error)

    return {
        "inserted": result.inserted,
        "inserted_count": len(result.inserted),
        "last_round": result.last_round,
        "last_draw_date": str(result.last_draw_date),
    }
