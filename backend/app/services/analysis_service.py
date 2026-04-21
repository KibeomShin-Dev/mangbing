"""
통계 분석 서비스 — Ver 2.3 기준
"""
import math
from app.models import LottoDraw, NumberStats


def compute_stats(draws: list[LottoDraw]) -> list[NumberStats]:
    """전체 회차 데이터를 받아 번호별 통계를 계산한다."""
    total = len(draws)
    if total == 0:
        return []

    recent_10 = draws[-10:] if total >= 10 else draws
    recent_30 = draws[-30:] if total >= 30 else draws
    recent_100 = draws[-100:] if total >= 100 else draws

    results = []
    for num in range(1, 46):
        total_count = sum(1 for d in draws if num in d.numbers)
        r10 = sum(1 for d in recent_10 if num in d.numbers)
        r30 = sum(1 for d in recent_30 if num in d.numbers)
        r100 = sum(1 for d in recent_100 if num in d.numbers)

        # cold_streak: 최근부터 역순으로 연속 미출현 횟수
        streak = 0
        for d in reversed(draws):
            if num in d.numbers:
                break
            streak += 1

        # Ver 2.3 구간 분류
        if streak <= 5:
            zone = "hot"
        elif streak <= 9:
            zone = "neutral"
        else:
            zone = "cold"

        # Ver 2.3 점수 모델
        score = _calc_score(num, streak, r10, r30, r100)

        results.append(
            NumberStats(
                number=num,
                total_count=total_count,
                recent_10_count=r10,
                recent_30_count=r30,
                recent_100_count=r100,
                cold_streak=streak,
                zone=zone,
                score=score,
            )
        )
    return results


def _calc_score(
    num: int,
    streak: int,
    recent_10: int,
    recent_30: int,
    recent_100: int,
) -> int:
    score = 0

    # Cold Streak 기본 점수
    if streak >= 30:
        score += 4
    elif streak >= 25:
        score += 5
    elif streak >= 20:
        score += 4
    elif streak >= 15:
        score += 3
    elif streak >= 10:
        score += 2
    elif streak >= 5:
        score += 1

    # Hot 활성화 보너스: streak≤5 AND 최근 10회 2회+
    if streak <= 5 and recent_10 >= 2:
        score += 1

    # 중립 구간 보너스
    if 6 <= streak <= 9:
        score += 1

    # Z-score 보너스 (최근 100회 기준, 기대값 100*6/45 ≈ 13.33)
    expected_100 = 100 * 6 / 45
    std_100 = math.sqrt(100 * (6 / 45) * (39 / 45))
    if std_100 > 0:
        z = (recent_100 - expected_100) / std_100
        if z > 1.5:
            score += 1

    # 저출현 보너스: 최근 30회 0~1회
    if recent_30 <= 1:
        score += 1

    # 과열 패널티: 최근 30회 8회+
    if recent_30 >= 8:
        score -= 1

    return max(score, 0)


def compute_balance_score(hot: int, neutral: int, cold: int) -> float:
    """균형 점수: 낮을수록 이상적 (0이 완벽)"""
    total = hot + neutral + cold
    if total == 0:
        return 100.0
    hot_pct = hot / total * 100
    neutral_pct = neutral / total * 100
    cold_pct = cold / total * 100
    return abs(hot_pct - 25) + abs(neutral_pct - 35) + abs(cold_pct - 40)
