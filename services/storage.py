import pandas as pd
from pathlib import Path
from app.config import CSV_PATH

COLUMNS = ["date", "type", "category", "description", "amount"]

def ensure_csv(path: Path = CSV_PATH):
    if not path.exists():
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(path, index=False, encoding="utf-8-sig")

def read_all(path: Path = CSV_PATH) -> pd.DataFrame:
    ensure_csv(path)
    return pd.read_csv(path, dtype={"date": str, "type": str, "category": str, "description": str, "amount": int})

def append_row(row: dict, path: Path = CSV_PATH):
    ensure_csv(path)
    df = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=COLUMNS)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")

def overwrite(df: pd.DataFrame, path: Path = CSV_PATH):
    df.to_csv(path, index=False, encoding="utf-8-sig")
