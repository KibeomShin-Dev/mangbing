"""
전략 리포트 서비스 — Ver 2.3 기준
JS report.js 로직을 Python으로 포팅
"""
import math
from app.models import (
    LottoDraw, NumberStats,
    StrategyScore, PersonaRec, NotableNumber,
    SegmentDist, HistComp, QualityGrade, ReportData,
)
from app.services.analysis_service import compute_stats, compute_balance_score
from app.services.strategy_service import recommend


# ── 전략 정의 ──────────────────────────────────────────────────────────────

STRATEGIES = [
    {'key': 'balanced',      'label': '⭐ 균형형',    'persona': 'balanced'},
    {'key': 'hotfocus',      'label': '🔥 Hot 집중형', 'persona': 'aggressive'},
    {'key': 'neutralfocus',  'label': '🎯 중립 집중형','persona': 'experimental'},
    {'key': 'coldfocus',     'label': '❄️ Cold 집중형','persona': 'conservative'},
    {'key': 'experimental',  'label': '🧪 실험형',    'persona': 'data'},
]

# 전략별 풀 구성 (각 구간에서 상위 N개 추출)
POOL_CONFIG = {
    'balanced':     {'hot': 4, 'neutral': 4, 'cold': 6},   # 14개
    'hotfocus':     {'hot': 6, 'neutral': 3, 'cold': 3},   # 12개
    'neutralfocus': {'hot': 3, 'neutral': 6, 'cold': 3},   # 12개
    'coldfocus':    {'hot': 3, 'neutral': 3, 'cold': 6},   # 12개
    'experimental': None,                                    # 전체 점수 상위 12개
}

# 전략별 이상적 구성 비율 (hot%, neutral%, cold%)
STRAT_COMP = {
    'balanced':     {'hot': 33.3, 'neutral': 33.3, 'cold': 33.3},
    'hotfocus':     {'hot': 50.0, 'neutral': 33.3, 'cold': 16.7},
    'neutralfocus': {'hot': 16.7, 'neutral': 50.0, 'cold': 33.3},
    'coldfocus':    {'hot': 16.7, 'neutral': 16.7, 'cold': 66.7},
    'experimental': None,
}


# ── 수학 유틸 ──────────────────────────────────────────────────────────────

def _hypergeom_at_least(N: int, K: int, n: int, min_hits: int) -> float:
    """P(X >= min_hits) — 초기하분포"""
    if K <= 0 or N <= 0:
        return 0.0
    denom = math.comb(N, n)
    if denom == 0:
        return 0.0
    prob = sum(
        math.comb(K, k) * math.comb(N - K, n - k) / denom
        for k in range(min_hits, min(n, K) + 1)
    )
    return min(1.0, max(0.0, prob))


# ── 풀 구성 ───────────────────────────────────────────────────────────────

def _get_pool(key: str, stats: list[NumberStats]) -> set[int]:
    hot_sorted     = sorted([s for s in stats if s.zone == 'hot'],     key=lambda s: -s.score)
    neutral_sorted = sorted([s for s in stats if s.zone == 'neutral'], key=lambda s: -s.score)
    cold_sorted    = sorted([s for s in stats if s.zone == 'cold'],    key=lambda s: -s.score)

    if key == 'experimental':
        top12 = sorted(stats, key=lambda s: -s.score)[:12]
        return {s.number for s in top12}

    cfg = POOL_CONFIG[key]
    return (
        {s.number for s in hot_sorted[:cfg['hot']]} |
        {s.number for s in neutral_sorted[:cfg['neutral']]} |
        {s.number for s in cold_sorted[:cfg['cold']]}
    )


def _pool_size(key: str) -> int:
    if key == 'experimental':
        return 12
    cfg = POOL_CONFIG[key]
    return cfg['hot'] + cfg['neutral'] + cfg['cold']


# ── 지표 계산 ─────────────────────────────────────────────────────────────

def _calc_pool_coverage(pool: set[int], draws: list[LottoDraw], n: int = 20) -> float:
    recent = draws[-n:]
    covered = total = 0
    for d in recent:
        for num in d.numbers:
            total += 1
            if num in pool:
                covered += 1
    return covered / total if total > 0 else 0.0


def _calc_comp_fit(key: str, hist_comp: dict) -> int:
    comp = STRAT_COMP.get(key)
    if not comp:
        return 65
    dev = (abs(comp['hot']     - hist_comp['hot']) +
           abs(comp['neutral'] - hist_comp['neutral']) +
           abs(comp['cold']    - hist_comp['cold']))
    return max(0, round(100 - dev * 0.5))


def _calc_situ_fit(key: str, seg_dist: SegmentDist) -> int:
    total = seg_dist.hot + seg_dist.neutral + seg_dist.cold
    if total == 0:
        return 50
    hot_pct  = seg_dist.hot     / total * 100
    neut_pct = seg_dist.neutral / total * 100
    cold_pct = seg_dist.cold    / total * 100
    comp = STRAT_COMP.get(key)
    if not comp:
        return 68
    dev = (abs(comp['hot']     - hot_pct) +
           abs(comp['neutral'] - neut_pct) +
           abs(comp['cold']    - cold_pct))
    return max(0, round(100 - dev * 0.4))


def _historical_win_comp(stats: list[NumberStats], draws: list[LottoDraw], n: int = 30) -> dict:
    zone_map = {s.number: s.zone for s in stats}
    recent = draws[-n:]
    hot = neutral = cold = 0
    for d in recent:
        for num in d.numbers:
            z = zone_map.get(num, 'neutral')
            if z == 'hot':       hot += 1
            elif z == 'neutral': neutral += 1
            else:                cold += 1
    total = hot + neutral + cold
    if total == 0:
        return {'hot': 33.3, 'neutral': 33.3, 'cold': 33.3}
    return {
        'hot':     round(hot     / total * 100, 1),
        'neutral': round(neutral / total * 100, 1),
        'cold':    round(cold    / total * 100, 1),
    }


def _calc_quality_score(stats: list[NumberStats]) -> int:
    score = 0
    score += sum(8 for s in stats if s.cold_streak >= 25)           # 극Cold
    score += sum(3 for s in stats if 15 <= s.cold_streak < 25)      # 강Cold
    score += sum(2 for s in stats if s.cold_streak <= 5 and s.recent_10_count >= 2)  # 활성 Hot
    neutral_cnt = sum(1 for s in stats if s.zone == 'neutral')
    score += min(neutral_cnt, 10)
    score += sum(2 for s in stats if s.score >= 4)                   # 고점수
    return min(score, 50)


def _quality_grade(score: int) -> QualityGrade:
    if score >= 30:
        return QualityGrade(score=score, grade='황금기', icon='🟢', desc='균형 공격 유리', color='#10b981')
    if score >= 20:
        return QualityGrade(score=score, grade='호황기', icon='🟡', desc='적극 추천',       color='#f59e0b')
    if score >= 10:
        return QualityGrade(score=score, grade='보통기', icon='🟠', desc='균형 유지',       color='#f97316')
    return     QualityGrade(score=score, grade='침체기', icon='🔴', desc='보수적 접근',     color='#ef4444')


# ── 메인 ──────────────────────────────────────────────────────────────────

def generate_report(draws: list[LottoDraw]) -> ReportData:
    stats = compute_stats(draws)
    stat_map = {s.number: s for s in stats}

    # 구간 분포
    seg_dist = SegmentDist(
        hot=sum(1 for s in stats if s.zone == 'hot'),
        neutral=sum(1 for s in stats if s.zone == 'neutral'),
        cold=sum(1 for s in stats if s.zone == 'cold'),
    )

    # 역사적 당첨 구성
    hc = _historical_win_comp(stats, draws, 30)
    hist_comp = HistComp(**hc)

    # 품질 점수
    q_score = _calc_quality_score(stats)
    quality = _quality_grade(q_score)

    # 전략별 점수
    strategy_scores: list[StrategyScore] = []
    for strat in STRATEGIES:
        key = strat['key']
        pool = _get_pool(key, stats)
        coverage = round(_calc_pool_coverage(pool, draws, 20) * 100)
        comp_fit = _calc_comp_fit(key, hc)
        situ_fit = _calc_situ_fit(key, seg_dist)
        total = round(coverage * 0.40 + comp_fit * 0.35 + situ_fit * 0.25)

        if total >= 72:   rank_label, rank_color = '강력 추천', '#10b981'
        elif total >= 62: rank_label, rank_color = '추천',     '#3b82f6'
        elif total >= 52: rank_label, rank_color = '보통',     '#f59e0b'
        else:             rank_label, rank_color = '비추천',   '#ef4444'

        strategy_scores.append(StrategyScore(
            key=key, label=strat['label'],
            coverage=coverage, comp_fit=comp_fit, situ_fit=situ_fit,
            total=total, rank_label=rank_label, rank_color=rank_color,
            pool_size=_pool_size(key),
        ))

    strategy_scores.sort(key=lambda s: -s.total)

    # 주목 Cold 번호 (streak≥10, 점수 순)
    top_cold = [
        NotableNumber(number=s.number, streak=s.cold_streak, score=s.score, recent_10=s.recent_10_count)
        for s in sorted([s for s in stats if s.cold_streak >= 10], key=lambda s: (-s.score, -s.cold_streak))[:5]
    ]

    # 주목 Hot 번호 (streak≤5, 최근10 2회+)
    top_hot = [
        NotableNumber(number=s.number, streak=s.cold_streak, score=s.score, recent_10=s.recent_10_count)
        for s in sorted([s for s in stats if s.cold_streak <= 5 and s.recent_10_count >= 2],
                        key=lambda s: (-s.recent_10_count, -s.score))[:5]
    ]

    # 성향별 추천
    # 정렬된 strategy_scores에서 persona 매핑
    persona_map = {s['persona']: next((sc for sc in strategy_scores if sc.key == s['key']), strategy_scores[0])
                   for s in STRATEGIES}

    # 페르소나별 추천 번호 1세트씩 생성
    def _make_persona_rec(title, icon, persona_key, reason) -> PersonaRec:
        sc = persona_map[persona_key]
        results = recommend(stats, strategy=sc.key, count=5)
        return PersonaRec(
            title=title, icon=icon,
            strategy=sc.key, label=sc.label,
            total=sc.total, reason=reason,
            sets=[{'numbers': r.numbers, 'hot_count': r.hot_count,
                   'neutral_count': r.neutral_count, 'cold_count': r.cold_count,
                   'balance_score': r.balance_score} for r in results],
        )

    personas = [
        _make_persona_rec('기본 (모든 분)', '👤', 'balanced',     '균형 잡힌 Hot/중립/Cold 배분으로 안정적.'),
        _make_persona_rec('공격적',         '⚔️', 'aggressive',   'Hot 번호 연속성·최근 흐름 중심 공략.'),
        _make_persona_rec('보수적',         '🛡️', 'conservative', 'Cold 번호 평균 회귀 기대, 장기 미출현 집중.'),
        _make_persona_rec('데이터 기반',    '🔬', 'data',          'V2.3 종합 점수 상위 번호 순수 통계 선택.'),
    ]

    last = draws[-1]
    return ReportData(
        total_draws=len(draws),
        last_round=last.round_no,
        last_draw_date=last.draw_date,
        next_round=last.round_no + 1,
        seg_dist=seg_dist,
        hist_comp=hist_comp,
        quality=quality,
        strategy_scores=strategy_scores,
        top_cold=top_cold,
        top_hot=top_hot,
        personas=personas,
    )
