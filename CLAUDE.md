# Mangbing — Claude 세션 컨텍스트

## 프로젝트 개요
한국 로또 6/45 번호 분석기. Python(FastAPI) 백엔드 + React(Vite) 프론트엔드.
- 백엔드: Render (https://mangbing-api.onrender.com)
- 프론트엔드: Vercel (https://mangbing.vercel.app)
- DB: Neon PostgreSQL (프로덕션) / SQLite (로컬 개발)

## 개발 서버 실행
```bash
# 백엔드 (포트 8000)
cd backend && uvicorn app.main:app --reload

# 프론트엔드 (포트 5173)
cd frontend && npm run dev
```

## DB 관리
```bash
# 초기화 (최초 1회, --force로 재초기화)
cd backend && python scripts/init_db.py
cd backend && python scripts/init_db.py --force

# 신규 회차 갱신 (dry-run으로 미리보기 가능)
cd backend && python scripts/update_db.py
cd backend && python scripts/update_db.py --dry-run
```

## 환경변수 (.env)
| 변수 | 설명 |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL 연결 문자열 (없으면 SQLite 폴백) |
| `FRONTEND_URL` | Vercel URL (CORS 허용, https:// 포함 필수) |
| `UPDATE_TOKEN` | `/api/lottery/update` 엔드포인트 인증 토큰 |

## 데이터 소스
- **초기 데이터**: `../lotto/asset/lottery_winning_numbers.md` (탭 구분: 회차 번1~6 보너스)
- **갱신 API**: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={회차}`
  - 응답 구조: `{ "data": { "list": [...] } }`
  - 응답 필드: `ltEpsd`(회차), `ltRflYmd`(추첨일 YYYYMMDD), `tm1WnNo~tm6WnNo`, `bnsWnNo`(보너스)
  - 미래 회차 → list 비어 있음 → 중단
  - User-Agent 헤더 필수 (없으면 서버가 차단)
- **DB 현황**: 마지막 수록 회차 1220 (2026-04-18 추첨)

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
| 전략 key | 레이블 | Hot | 중립 | Cold |
|---|---|---|---|---|
| balanced | 균형형 | 2 | 2 | 2 |
| hotfocus | Hot 집중형 | 3 | 2 | 1 |
| neutralfocus | 중립 집중형 | 1 | 3 | 2 |
| coldfocus | Cold 집중형 | 1 | 1 | 4 |
| experimental | 실험형 | 2 | 1 | 3 |

### 균형 점수
`|Hot%-25| + |중립%-35| + |Cold%-40|` → 0에 가까울수록 이상적

## 전체 API 엔드포인트
```
GET  /api/lottery/status          → DBStatus
GET  /api/lottery/?limit=N        → LottoDraw[]
GET  /api/lottery/all             → LottoDraw[]
GET  /api/lottery/{round_no}      → LottoDraw
POST /api/lottery/update          → 신규 회차 갱신 (X-Update-Token 헤더 필요)
GET  /api/analysis/stats          → NumberStats[]
GET  /api/analysis/report         → ReportData (전략 리포트 + 페르소나별 추천 5세트)
POST /api/strategy/recommend      → StrategyResult[]
```

## 프론트엔드 탭 구성
1. **DB 현황** (`DBPage.jsx`) — DB 상태 + 최근 20회차 볼 표시
2. **통계 분석** (`AnalysisPage.jsx`) — 번호별 Hot/중립/Cold 통계 테이블
3. **번호 추천** (`RecommendPage.jsx`) — 전략 선택 + 조합 수 선택 + 추천
4. **전략 리포트** (`ReportPage.jsx`) — 시장 상황, 전략 적합도, 주목 번호, 성향별 5세트 추천

## 주요 파일 구조
```
backend/
  app/
    main.py              # FastAPI + CORS (FRONTEND_URL 동적 등록)
    database.py          # DATABASE_URL 있으면 PostgreSQL, 없으면 SQLite
    models.py            # DB 모델 + Pydantic 스키마 (NumberSet, PersonaRec 등)
    routers/
      lottery.py         # 회차 CRUD + POST /update
      analysis.py        # stats + report
      strategy.py        # recommend
    services/
      lottery_service.py
      analysis_service.py
      strategy_service.py
      report_service.py  # 리포트 생성 (초기하분포, 전략 적합도, 페르소나 추천)
      update_service.py  # API 호출 로직 (스크립트·엔드포인트 공유)
  scripts/
    init_db.py           # MD 파일 → DB 초기화
    update_db.py         # 신규 회차 갱신 스크립트
frontend/
  src/
    api/lottery.js       # axios 호출 함수 (VITE_API_BASE_URL 환경변수)
    pages/               # DBPage, AnalysisPage, RecommendPage, ReportPage
.github/workflows/
  update-db.yml          # 매주 일요일 10시(KST) 자동 갱신
```

## 배포 환경변수 체크리스트
| 위치 | 변수 | 값 |
|---|---|---|
| Render | DATABASE_URL | Neon 연결 문자열 |
| Render | FRONTEND_URL | https://mangbing.vercel.app |
| Render | UPDATE_TOKEN | 비밀 토큰 |
| Vercel | VITE_API_BASE_URL | https://mangbing-api.onrender.com |
| GitHub Secrets | BACKEND_URL | https://mangbing-api.onrender.com |
| GitHub Secrets | UPDATE_TOKEN | 비밀 토큰 (Render와 동일) |

## 기술 결정사항
- Pydantic v2 (`model_config`, `computed_field`)
- 로컬 개발: Vite 프록시로 CORS 불필요
- Render 무료 티어: 15분 비활성 시 슬립 (콜드스타트 ~30초)
- CORS origins: `https://` 포함 정확히 입력 필요 (trailing slash 금지)
