

from pathlib import Path
# 경로/카테고리/날짜 포맷과 UI 색상 등 공통 설정을 모아둔 파일
# 프로젝트 루트: config.py 기준으로 상위 디렉터리 두 단계
BASE_DIR = Path(__file__).resolve().parents[1]

# 데이터 저장 디렉토리: 없으면 생성
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# CSV 파일 경로
CSV_PATH = DATA_DIR / "transactions.csv"

# 기본 카테고리
CATEGORIES = ["식비", "교통", "생활/통신", "쇼핑", "문화/여가", "교육", "의료/건강", "기타"]

# 표시/검증에 사용할 날짜 포맷
DATE_FMT = "%Y-%m-%d"  # 예: 2025-08-18

# ===== UI 스타일 값들 =====
FONT_FAMILY = "맑은 고딕"  # Windows에서 한글 가독성 좋음
FONT_SIZE = 10
ROW_HEIGHT = 26

# 라이트 테마 색상
COLOR_BG = "#F7F8FA"
COLOR_PANEL = "#EEEFF3"
COLOR_BORDER = "#D7D9DE"
COLOR_TEXT = "#1F2937"
COLOR_ACCENT = "#4F46E5"   # 포인트 색
COLOR_INC = "#059669"      # 수입(초록)
COLOR_EXP = "#DC2626"      # 지출(빨강)
COLOR_STRIPE = "#F2F4F7"   # 표 줄무늬
