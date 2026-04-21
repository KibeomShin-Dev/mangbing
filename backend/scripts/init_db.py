"""
초기 DB 구성 스크립트
사용법: python -m scripts.init_db [--data-file PATH]

기본 데이터 파일 경로: ../../../lotto/asset/lottery_winning_numbers.md
(현재 프로젝트 기준 상대 경로)

데이터 파일 형식 (탭 구분):
  회차  번1  번2  번3  번4  번5  번6  보너스
예) 1218	3	28	31	32	42	45	25
"""
import sys
import argparse
from pathlib import Path
from datetime import date

# 프로젝트 루트(backend/)를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine, SessionLocal
from app.models import Base, LottoDrawDB

# 추첨 날짜 역산용 기준점
# 1회차: 2002-12-07 (토요일)
FIRST_DRAW_DATE = date(2002, 12, 7)
DRAW_INTERVAL_DAYS = 7


def round_to_date(round_no: int) -> date:
    """회차 번호로 추첨일 계산 (근사값, 실제 특별 회차 제외)"""
    from datetime import timedelta
    return FIRST_DRAW_DATE + timedelta(days=(round_no - 1) * DRAW_INTERVAL_DAYS)


def parse_data_file(path: Path) -> list[dict]:
    draws = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 8:
                print(f"  [skip] 형식 오류: {line!r}")
                continue
            try:
                round_no = int(parts[0])
                nums = [int(x) for x in parts[1:]]
                draws.append({
                    "round_no": round_no,
                    "draw_date": round_to_date(round_no),
                    "num1": nums[0],
                    "num2": nums[1],
                    "num3": nums[2],
                    "num4": nums[3],
                    "num5": nums[4],
                    "num6": nums[5],
                    "bonus": nums[6],
                })
            except ValueError as e:
                print(f"  [skip] 파싱 오류: {line!r} → {e}")
    return draws


def main():
    parser = argparse.ArgumentParser(description="로또 DB 초기화")
    default_data = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "lotto" / "asset" / "lottery_winning_numbers.md"
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=default_data,
        help=f"데이터 파일 경로 (기본: {default_data})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="기존 데이터 삭제 후 재삽입",
    )
    args = parser.parse_args()

    if not args.data_file.exists():
        print(f"[오류] 데이터 파일을 찾을 수 없습니다: {args.data_file}")
        print("  --data-file 옵션으로 경로를 지정해 주세요.")
        sys.exit(1)

    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing = db.query(LottoDrawDB).count()
        if existing > 0 and not args.force:
            print(f"[info] DB에 이미 {existing}개 회차 데이터가 있습니다.")
            print("  덮어쓰려면 --force 옵션을 사용하세요.")
            return

        if args.force:
            db.query(LottoDrawDB).delete()
            db.commit()
            print("[info] 기존 데이터 삭제 완료")

        print(f"[info] 데이터 파일 파싱 중: {args.data_file}")
        draws = parse_data_file(args.data_file)
        print(f"[info] {len(draws)}개 회차 파싱 완료")

        for d in draws:
            db.add(LottoDrawDB(**d))
        db.commit()
        print(f"[완료] {len(draws)}개 회차 DB 삽입 완료")

        # 마지막 회차 확인
        from sqlalchemy import desc
        last = db.query(LottoDrawDB).order_by(desc(LottoDrawDB.round_no)).first()
        print(f"  → 최신 회차: {last.round_no}회 ({last.draw_date})")

    finally:
        db.close()


if __name__ == "__main__":
    main()
