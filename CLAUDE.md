# Mangbing — Claude 세션 컨텍스트

## 프로젝트 개요
한국 로또 6/45 번호 분석기. Python(FastAPI) 백엔드 + React(Vite) 프론트엔드.
기존 순수 JS 앱(lotto/)을 Python + React로 재구성한 버전.

## 개발 서버 실행
```bash
# 백엔드 (포트 8000)
cd backend && uvicorn app.main:app --reload

# 프론트엔드 (포트 5173)
cd frontend && npm run dev
```

## DB 관리
```bash
# 초기화 (최초 1회)
cd backend && python scripts/init_db.py

# 신규 회차 갱신
cd backend && python scripts/update_db.py
```

## 데이터 소스
- **초기 데이터**: `../lotto/asset/lottery_winning_numbers.md` (탭 구분: 회차 번1~6 보너스)
- **API 갱신**: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={회차}`
  - `srchDir=center`: 해당 회차 전후 최대 10개 반환 (리스트)
  - 응답 필드: `ltEpsd`(회차), `ltRflYmd`(추첨일 YYYYMMDD), `tm1WnNo~tm6WnNo`(당첨번호), `bnsWnNo`(보너스)
  - 미래 회차 요청 시 null/빈 응답 → 중단
- **DB 현황**: SQLite (`backend/lotto.db`), 마지막 수록 회차 1218 (2026-04-04 추첨)

## Ver 2.3 핵심 설계 원칙

### 구간 분류 (cold_streak 기준)
- **Hot**: 0~5회 연속 미출현
- **중립**: 6~9회 연속 미출현
- **Cold**: 10회+ 연속 미출현

### 균형 배분 목표
`Hot 25% : 중립 35% : Cold 40%` → 6개 중 Hot 2 + 중립 2 + Cold 2

### 점수 모델 (`analysis_service.py`)
| Cold Streak | 기본 점수 |
|---|---|
| 25~29회 | 5 |
| 20~24 / 30+ | 4 |
| 15~19 | 3 |
| 10~14 | 2 |
| 5~9 | 1 |
| 0~4 | 0 |

보너스/패널티:
- Hot 활성화: streak≤5 AND 최근10회 2회+ → +1
- 중립 구간: streak 6~9 → +1
- Z-score: 최근100회 Z>1.5 → +1
- 저출현: 최근30회 0~1회 → +1
- 과열 패널티: 최근30회 8회+ → -1

### 5가지 전략 (`strategy_service.py`)
| 전략 | Hot | 중립 | Cold |
|---|---|---|---|
| balanced | 2 | 2 | 2 |
| hotfocus | 3 | 2 | 1 |
| neutralfocus | 1 | 3 | 2 |
| coldfocus | 1 | 1 | 4 |
| experimental | 2 | 1 | 3 |

### 균형 점수 계산
`|Hot%-25| + |중립%-35| + |Cold%-40|` → 0에 가까울수록 이상적

## API 엔드포인트 구조
```
GET  /api/lottery/status          → DBStatus
GET  /api/lottery/?limit=N        → LottoDraw[]
GET  /api/lottery/all             → LottoDraw[]
GET  /api/lottery/{round_no}      → LottoDraw
GET  /api/analysis/stats          → NumberStats[]
POST /api/strategy/recommend      → StrategyResult[]
```

## 주요 설계 결정사항
- DB: SQLite + SQLAlchemy (단일 사용자, 서버 불필요)
- 프론트↔백엔드 통신: Vite 프록시 (`/api` → `localhost:8000`) → CORS 불필요
- 갱신 스크립트: 날짜 기반 추산 + 개별 API 호출 방식 (회차당 0.5초 딜레이)
- Pydantic v2 사용 (`model_config`, `computed_field`)
