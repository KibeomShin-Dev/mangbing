from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import LottoDrawDB, LottoDraw, DBStatus
from datetime import date


def get_all_draws(db: Session) -> list[LottoDraw]:
    rows = db.query(LottoDrawDB).order_by(LottoDrawDB.round_no).all()
    return [LottoDraw.model_validate(r) for r in rows]


def get_recent_draws(db: Session, n: int = 100) -> list[LottoDraw]:
    rows = (
        db.query(LottoDrawDB)
        .order_by(desc(LottoDrawDB.round_no))
        .limit(n)
        .all()
    )
    return [LottoDraw.model_validate(r) for r in reversed(rows)]


def get_draw(db: Session, round_no: int) -> LottoDraw | None:
    row = db.query(LottoDrawDB).filter(LottoDrawDB.round_no == round_no).first()
    return LottoDraw.model_validate(row) if row else None


def get_db_status(db: Session) -> DBStatus | None:
    total = db.query(LottoDrawDB).count()
    if total == 0:
        return None
    last = db.query(LottoDrawDB).order_by(desc(LottoDrawDB.round_no)).first()
    first = db.query(LottoDrawDB).order_by(LottoDrawDB.round_no).first()
    return DBStatus(
        total_rounds=total,
        last_round=last.round_no,
        last_draw_date=last.draw_date,
        first_round=first.round_no,
    )


def upsert_draw(db: Session, draw: LottoDraw) -> bool:
    """Insert or update a draw. Returns True if inserted (new), False if updated."""
    existing = db.query(LottoDrawDB).filter(LottoDrawDB.round_no == draw.round_no).first()
    if existing:
        for field in ["draw_date", "num1", "num2", "num3", "num4", "num5", "num6", "bonus"]:
            setattr(existing, field, getattr(draw, field))
        db.commit()
        return False
    else:
        row = LottoDrawDB(**draw.model_dump(exclude={"numbers"}))
        db.add(row)
        db.commit()
        return True
