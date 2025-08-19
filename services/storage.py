

import pandas as pd
from pathlib import Path
from app.config import CSV_PATH
# CSV 파일을 읽고/쓰는 저장소(Repository) 역할
# CSV 컬럼 순서(표시/저장 통일)
COLUMNS = ["date", "type", "category", "description", "amount"]

def ensure_csv(path: Path = CSV_PATH):
    """
    CSV가 없으면 헤더만 가진 빈 파일을 생성.
    과제/발표 시 초기 실행이 편하게 하려는 목적.
    """
    if not path.exists():
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(path, index=False, encoding="utf-8-sig")

def read_all(path: Path = CSV_PATH) -> pd.DataFrame:
    """
    CSV 전체를 읽어 DataFrame으로 반환.
    dtype을 명시해 문자열/정수 타입이 틀어지지 않게 함.
    """
    ensure_csv(path)
    return pd.read_csv(
        path,
        dtype={"date": str, "type": str, "category": str, "description": str, "amount": int}
    )

def append_row(row: dict, path: Path = CSV_PATH):
    """
    한 줄(row)을 CSV 뒤에 추가 저장.
    - row는 COLUMNS 키를 모두 포함한 dict여야 함.
    """
    ensure_csv(path)
    df = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=COLUMNS)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")

def overwrite(df: pd.DataFrame, path: Path = CSV_PATH):
    """
    현재 DataFrame을 CSV로 완전히 덮어쓰기.
    - 삭제/정렬 후 저장할 때 사용.
    """
    df.to_csv(path, index=False, encoding="utf-8-sig")
