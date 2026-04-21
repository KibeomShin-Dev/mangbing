"""
번호 추천 전략 서비스 — Ver 2.3 균형 전략
"""
import random
from app.models import NumberStats, StrategyResult
from app.services.analysis_service import compute_balance_score

# 전략별 목표 배분 (hot, neutral, cold)
STRATEGY_TARGETS = {
    "balanced":      (2, 2, 2),   # 균형형: Hot 25% / 중립 35% / Cold 40% 근사
    "hotfocus":      (3, 2, 1),
    "neutralfocus":  (1, 3, 2),
    "coldfocus":     (1, 1, 4),
    "experimental":  (2, 1, 3),
}


def recommend(
    stats: list[NumberStats],
    strategy: str = "balanced",
    count: int = 5,
) -> list[StrategyResult]:
    target = STRATEGY_TARGETS.get(strategy, STRATEGY_TARGETS["balanced"])
    hot_n, neutral_n, cold_n = target

    hot_pool = [s for s in stats if s.zone == "hot"]
    neutral_pool = [s for s in stats if s.zone == "neutral"]
    cold_pool = [s for s in stats if s.zone == "cold"]

    results = []
    for _ in range(count):
        combo = _pick_combo(hot_pool, neutral_pool, cold_pool, hot_n, neutral_n, cold_n)
        numbers = sorted(combo)
        hot_cnt = sum(1 for n in numbers if _zone(n, stats) == "hot")
        neutral_cnt = sum(1 for n in numbers if _zone(n, stats) == "neutral")
        cold_cnt = sum(1 for n in numbers if _zone(n, stats) == "cold")
        balance = compute_balance_score(hot_cnt, neutral_cnt, cold_cnt)
        results.append(
            StrategyResult(
                strategy=strategy,
                numbers=numbers,
                hot_count=hot_cnt,
                neutral_count=neutral_cnt,
                cold_count=cold_cnt,
                balance_score=round(balance, 2),
            )
        )
    return results


def _pick_combo(
    hot_pool: list[NumberStats],
    neutral_pool: list[NumberStats],
    cold_pool: list[NumberStats],
    hot_n: int,
    neutral_n: int,
    cold_n: int,
) -> list[int]:
    """가중치 기반 무작위 추출 (스코어 비례)"""
    selected = set()

    def weighted_pick(pool: list[NumberStats], n: int) -> list[int]:
        available = [s for s in pool if s.number not in selected]
        if len(available) < n:
            # 부족한 경우 전체 pool에서 보충
            all_pool = hot_pool + neutral_pool + cold_pool
            available = [s for s in all_pool if s.number not in selected]
        weights = [max(s.score, 1) for s in available]
        chosen = random.choices(available, weights=weights, k=min(n, len(available)))
        # 중복 제거
        unique = []
        seen = set()
        for c in chosen:
            if c.number not in seen and c.number not in selected:
                unique.append(c.number)
                seen.add(c.number)
        # 부족하면 나머지에서 채움
        while len(unique) < n:
            remaining = [s for s in available if s.number not in selected and s.number not in seen]
            if not remaining:
                break
            extra = random.choice(remaining)
            unique.append(extra.number)
            seen.add(extra.number)
        return unique[:n]

    hot_picks = weighted_pick(hot_pool, hot_n)
    selected.update(hot_picks)
    neutral_picks = weighted_pick(neutral_pool, neutral_n)
    selected.update(neutral_picks)
    cold_picks = weighted_pick(cold_pool, cold_n)
    selected.update(cold_picks)

    combo = hot_picks + neutral_picks + cold_picks
    # 혹시 6개가 안 되면 나머지에서 보충
    all_pool = hot_pool + neutral_pool + cold_pool
    while len(combo) < 6:
        remaining = [s for s in all_pool if s.number not in selected]
        if not remaining:
            break
        extra = random.choice(remaining)
        combo.append(extra.number)
        selected.add(extra.number)
    return combo[:6]


def _zone(number: int, stats: list[NumberStats]) -> str:
    for s in stats:
        if s.number == number:
            return s.zone
    return "neutral"
