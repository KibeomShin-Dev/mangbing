from sqlalchemy import Column, Integer, Date
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel, computed_field
from datetime import date
from typing import Optional


class Base(DeclarativeBase):
    pass


class LottoDrawDB(Base):
    __tablename__ = "lotto_draws"

    round_no = Column(Integer, primary_key=True, index=True)
    draw_date = Column(Date, nullable=False)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    num4 = Column(Integer, nullable=False)
    num5 = Column(Integer, nullable=False)
    num6 = Column(Integer, nullable=False)
    bonus = Column(Integer, nullable=False)


class LottoDraw(BaseModel):
    round_no: int
    draw_date: date
    num1: int
    num2: int
    num3: int
    num4: int
    num5: int
    num6: int
    bonus: int

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def numbers(self) -> list[int]:
        return [self.num1, self.num2, self.num3, self.num4, self.num5, self.num6]


class DBStatus(BaseModel):
    total_rounds: int
    last_round: int
    last_draw_date: date
    first_round: int


class NumberStats(BaseModel):
    number: int
    total_count: int
    recent_10_count: int
    recent_30_count: int
    recent_100_count: int
    cold_streak: int
    zone: str  # "hot" | "neutral" | "cold"
    score: int


class StrategyRequest(BaseModel):
    strategy: str = "balanced"  # balanced | hotfocus | neutralfocus | coldfocus | experimental
    count: int = 5  # 추천 조합 수


class StrategyResult(BaseModel):
    strategy: str
    numbers: list[int]
    hot_count: int
    neutral_count: int
    cold_count: int
    balance_score: float
