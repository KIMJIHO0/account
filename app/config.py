from pathlib import Path

# 기본 경로
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 사용자/세션 파일
USERS_CSV = DATA_DIR / "users.csv"

# 기존 설정들
DATE_FMT = "%Y-%m-%d"
CSV_PATH = DATA_DIR / "transactions.csv"  # (레거시용, 안 씀) 사용자별로 분기 저장

# 색상(심플 톤)
COLOR_BG = "#f7f7fa"
COLOR_PANEL = "#f0f2f5"
COLOR_BORDER = "#d9d9e3"
COLOR_ACCENT = "#6366f1"   # 인디고
COLOR_INC = "#059669"      # 초록
COLOR_EXP = "#dc2626"      # 빨강
COLOR_STRIPE = "#fafbff"

# 카테고리
CATEGORIES = [
    "식비", "교통", "주거/관리", "통신", "여가/문화", "의료/건강",
    "교육", "금융", "쇼핑", "기타", "월급", "용돈", "투자수익"
]
