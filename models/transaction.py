

from dataclasses import dataclass
from datetime import datetime
from app.config import DATE_FMT
# 한 건의 거래(수입/지출)를 표현하는 데이터 모델과 검증 로직
@dataclass
class Transaction:
    """
    한 줄의 거래를 표현
    - date: YYYY-MM-DD (문자열)
    - type: "수입" 또는 "지출"
    - category: 카테고리명
    - description: 설명
    - amount: 금액(정수, 원화)
    """
    date: str
    type: str
    category: str
    description: str
    amount: int

    @staticmethod
    def validate(tx: "Transaction"):
        """
        입력값 간단 검증:
        - 날짜 형식이 맞는지
        - type이 '수입'/'지출' 중 하나인지
        - 금액이 정수인지
        """
        # 날짜 형식 검증 (형식이 틀리면 ValueError 발생)
        datetime.strptime(tx.date, DATE_FMT)
        if tx.type not in ("수입", "지출"):
            raise ValueError("type은 '수입' 또는 '지출'이어야 합니다.")
        if not isinstance(tx.amount, int):
            raise ValueError("amount는 정수여야 합니다.")
