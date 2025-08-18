from pathlib import Path

# 프로젝트 루트
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CSV_PATH = DATA_DIR / "transactions.csv"

CATEGORIES = ["식비", "교통", "생활/통신", "쇼핑", "문화/여가", "교육", "의료/건강", "기타"]
CURRENCY = "KRW"
DATE_FMT = "%Y-%m-%d"   # 예: 2025-08-18

# ===== UI 스타일 기본값 =====
FONT_FAMILY = "맑은 고딕"  # Windows 권장(한글 가독성)
FONT_SIZE = 10
ROW_HEIGHT = 26

# 색상 팔레트 (연한 라이트 테마)
COLOR_BG = "#F7F8FA"
COLOR_PANEL = "#EEEFF3"
COLOR_BORDER = "#D7D9DE"
COLOR_TEXT = "#1F2937"
COLOR_ACCENT = "#4F46E5"   # 보라톤 포인트
COLOR_INC = "#059669"      # 수입(녹색)
COLOR_EXP = "#DC2626"      # 지출(빨강)
COLOR_STRIPE = "#F2F4F7"   # 테이블 줄무늬
