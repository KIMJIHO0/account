import pandas as pd
from pathlib import Path
from typing import Dict
from app.config import DATA_DIR

def csv_path_for_user(username: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / f"transactions_{username}.csv"

def _ensure_csv(path: Path):
    if not path.exists():
        path.write_text("date,type,category,description,amount\n", encoding="utf-8")

def read_all(path: Path) -> pd.DataFrame:
    _ensure_csv(path)
    return pd.read_csv(path, dtype=str).fillna("")

def append_row(row: Dict, path: Path):
    df = read_all(path)
    # 타입 맞춤
    row = {
        "date": row.get("date", ""),
        "type": row.get("type", ""),
        "category": row.get("category", ""),
        "description": row.get("description", ""),
        "amount": str(row.get("amount", "0")),
    }
    df.loc[len(df)] = row
    df.to_csv(path, index=False, encoding="utf-8")

def overwrite(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False, encoding="utf-8")
