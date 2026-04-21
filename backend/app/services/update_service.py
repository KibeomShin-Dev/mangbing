"""
DB 갱신 서비스 — update_db.py 스크립트와 /api/lottery/update 엔드포인트가 공유
"""
import time
from datetime import date, datetime

import httpx
from sqlalchemy.orm import Session

from app.models import LottoDraw
from app.services.lottery_service import upsert_draw, get_db_status

API_URL = "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do"
REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.dhlottery.co.kr/",
}


def fetch_draw(round_no: int) -> dict | None:
    try:
        resp = httpx.get(
            API_URL,
            params={"srchDir": "center", "srchLtEpsd": round_no},
            headers=HEADERS,
            timeout=10.0,
        )
        resp.raise_for_status()
        payload = resp.json()
        rows = (payload or {}).get("data", {}) or {}
        rows = rows.get("list") or []
        for row in rows:
            if int(row.get("ltEpsd", -1)) == round_no:
                return row
        return None
    except Exception:
        return None


def parse_row(data: dict) -> LottoDraw:
    return LottoDraw(
        round_no=int(data["ltEpsd"]),
        draw_date=datetime.strptime(str(data["ltRflYmd"]), "%Y%m%d").date(),
        num1=int(data["tm1WnNo"]),
        num2=int(data["tm2WnNo"]),
        num3=int(data["tm3WnNo"]),
        num4=int(data["tm4WnNo"]),
        num5=int(data["tm5WnNo"]),
        num6=int(data["tm6WnNo"]),
        bonus=int(data["bnsWnNo"]),
    )


def estimate_new_rounds(last_draw_date: date, today: date | None = None) -> int:
    today = today or date.today()
    days_elapsed = (today - last_draw_date).days
    return (days_elapsed // 7) + 2


class UpdateResult:
    def __init__(self):
        self.inserted: list[int] = []
        self.last_round: int | None = None
        self.last_draw_date: date | None = None
        self.error: str | None = None


def run_update(db: Session) -> UpdateResult:
    result = UpdateResult()
    status = get_db_status(db)
    if not status:
        result.error = "DB가 비어 있습니다."
        return result

    last_round = status.last_round
    max_tries = estimate_new_rounds(status.last_draw_date)

    for offset in range(1, max_tries + 1):
        target = last_round + offset
        data = fetch_draw(target)
        if data is None:
            break
        draw = parse_row(data)
        is_new = upsert_draw(db, draw)
        if is_new:
            result.inserted.append(target)
        time.sleep(REQUEST_DELAY)

    new_status = get_db_status(db)
    if new_status:
        result.last_round = new_status.last_round
        result.last_draw_date = new_status.last_draw_date

    return result
