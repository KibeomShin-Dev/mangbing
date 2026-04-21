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


class StrategyScore(BaseModel):
    key: str
    label: str
    coverage: int        # 풀 커버리지 % (0-100)
    comp_fit: int        # 구성 적합도 (0-100)
    situ_fit: int        # 상황 적합도 (0-100)
    total: int           # 종합 점수 (0-100)
    rank_label: str      # 강력 추천 | 추천 | 보통 | 비추천
    rank_color: str
    pool_size: int


class PersonaRec(BaseModel):
    title: str
    icon: str
    strategy: str
    label: str
    total: int
    reason: str
    numbers: list[int]       # 추천 번호 세트
    hot_count: int
    neutral_count: int
    cold_count: int
    balance_score: float


class NotableNumber(BaseModel):
    number: int
    streak: int
    score: int
    recent_10: int


class SegmentDist(BaseModel):
    hot: int
    neutral: int
    cold: int


class HistComp(BaseModel):
    hot: float
    neutral: float
    cold: float


class QualityGrade(BaseModel):
    score: int
    grade: str   # 황금기 | 호황기 | 보통기 | 침체기
    icon: str
    desc: str
    color: str


class ReportData(BaseModel):
    total_draws: int
    last_round: int
    last_draw_date: date
    next_round: int
    seg_dist: SegmentDist
    hist_comp: HistComp
    quality: QualityGrade
    strategy_scores: list[StrategyScore]
    top_cold: list[NotableNumber]
    top_hot: list[NotableNumber]
    personas: list[PersonaRec]


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
