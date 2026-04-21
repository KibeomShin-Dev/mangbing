# Mangbing — 로또 분석기

## 프로젝트 구조

```
mangbing/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 (포트 8000)
│   │   ├── database.py          # SQLite 연결 (SQLAlchemy)
│   │   ├── models.py            # DB 모델 + Pydantic 스키마
│   │   ├── routers/             # API 라우터
│   │   │   ├── lottery.py       # GET /api/lottery/...
│   │   │   ├── analysis.py      # GET /api/analysis/stats
│   │   │   └── strategy.py      # POST /api/strategy/recommend
│   │   └── services/            # 비즈니스 로직
│   │       ├── lottery_service.py
│   │       ├── analysis_service.py   # Ver 2.3 통계
│   │       └── strategy_service.py   # Ver 2.3 전략
│   ├── scripts/
│   │   ├── init_db.py           # 초기 데이터 MD 파일 → DB
│   │   └── update_db.py         # 동행복권 API → 신규 회차 저장
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/lottery.js       # axios API 호출 함수
    │   ├── pages/
    │   │   ├── DBPage.jsx        # DB 현황 + 최근 회차
    │   │   ├── AnalysisPage.jsx  # 번호별 통계 테이블
    │   │   └── RecommendPage.jsx # 전략 선택 + 번호 추천
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    └── vite.config.js           # /api → localhost:8000 프록시
```

---

## 최초 셋업

### 백엔드

```bash
cd backend

# 의존성 설치 (pip)
pip install -r requirements.txt

# .env 파일 생성 (선택 — 기본값으로도 동작)
copy .env.example .env

# DB 초기화 (asset/lottery_winning_numbers.md 에서 읽어옴)
python scripts/init_db.py

# 다른 경로에 데이터 파일이 있을 경우
python scripts/init_db.py --data-file "C:/path/to/lottery_winning_numbers.md"
```

### 프론트엔드

```bash
cd frontend
npm install
```

---

## 개발 서버 실행

터미널 2개 필요:

```bash
# 터미널 1 — 백엔드
cd backend
uvicorn app.main:app --reload

# 터미널 2 — 프론트엔드
cd frontend
npm run dev
```

브라우저: http://localhost:5173

---

## DB 갱신 (신규 회차 추가)

```bash
cd backend

# 실제 갱신
python scripts/update_db.py

# 저장 없이 미리보기
python scripts/update_db.py --dry-run
```

**갱신 로직:**
- DB의 마지막 회차 날짜와 오늘을 비교 → 추가 추첨 횟수 추산
- `https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=ROUND` 호출
- `returnValue == "success"` 이면 저장, 그 외 중단

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/lottery/status` | DB 현황 (총 회차, 최신 회차 등) |
| GET | `/api/lottery/` | 최근 100회차 목록 (`?limit=N`) |
| GET | `/api/lottery/all` | 전체 회차 목록 |
| GET | `/api/lottery/{round_no}` | 특정 회차 조회 |
| GET | `/api/analysis/stats` | 번호별 통계 (Ver 2.3) |
| POST | `/api/strategy/recommend` | 번호 추천 (전략 + 개수 지정) |

Swagger UI: http://localhost:8000/docs
