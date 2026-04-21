"""
DB 갱신 스크립트 — 동행복권 API에서 신규 회차 가져오기
사용법: python scripts/update_db.py [--dry-run]

API: https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={회차}
  응답 구조: { "data": { "list": [...] } }
  미래 회차 요청 시 list가 비거나 해당 회차 항목 없음 → 중단
"""
import sys
import time
import argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine, SessionLocal
from app.models import Base
from app.services.lottery_service import get_db_status, upsert_draw
from app.services.update_service import fetch_draw, parse_row, estimate_new_rounds


def main():
    parser = argparse.ArgumentParser(description="로또 DB 신규 회차 갱신")
    parser.add_argument("--dry-run", action="store_true", help="실제 저장 없이 결과만 출력")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        status = get_db_status(db)
        if not status:
            print("[오류] DB가 비어 있습니다. 먼저 python scripts/init_db.py를 실행하세요.")
            sys.exit(1)

        last_round = status.last_round
        today = date.today()
        max_tries = estimate_new_rounds(status.last_draw_date, today)

        print(f"[info] DB 현황: {status.total_rounds}회차 수록 (최신: {last_round}회, {status.last_draw_date})")
        print(f"[info] 오늘 날짜: {today}")
        print(f"[info] 최대 {max_tries}회차 시도 예정 ({last_round+1} ~ {last_round+max_tries})")

        inserted = 0
        for offset in range(1, max_tries + 1):
            target = last_round + offset
            print(f"  → {target}회 조회 중...", end=" ")
            data = fetch_draw(target)

            if data is None:
                print("없음 (미래 회차 또는 오류) — 중단")
                break

            draw = parse_row(data)
            print(f"당첨번호: {draw.numbers} 보너스: {draw.bonus} ({draw.draw_date})", end=" ")

            if args.dry_run:
                print("[dry-run, 저장 생략]")
            else:
                is_new = upsert_draw(db, draw)
                print("[신규 저장]" if is_new else "[업데이트]")
                if is_new:
                    inserted += 1

            time.sleep(0.5)

        if args.dry_run:
            print("\n[dry-run 완료] 실제 저장 없음")
        else:
            print(f"\n[완료] {inserted}개 신규 회차 저장")
            if inserted > 0:
                new_status = get_db_status(db)
                print(f"  → 최신 회차: {new_status.last_round}회 ({new_status.last_draw_date})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
