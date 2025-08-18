from pathlib import Path

# 프로젝트 루트 기준 상대 경로
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CSV_PATH = DATA_DIR / "transactions.csv"

CATEGORIES = ["식비", "교통", "생활/통신", "쇼핑", "문화/여가", "교육", "의료/건강", "기타"]
CURRENCY = "KRW"
DATE_FMT = "%Y-%m-%d"  # 입력/표시 날짜 형식
