from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    date: str       # "YYYY-MM-DD"
    type: str       # "수입" or "지출"
    category: str
    description: str
    amount: int     # 원화 정수

    @staticmethod
    def validate(tx: "Transaction"):
        # 간단 검증
        from app.config import DATE_FMT
        datetime.strptime(tx.date, DATE_FMT)
        if tx.type not in ("수입", "지출"):
            raise ValueError("type은 '수입' 또는 '지출'이어야 합니다.")
        if not isinstance(tx.amount, int):
            raise ValueError("amount는 정수여야 합니다.")
