import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import pandas as pd  # 날짜 인덱스 변환용

# ✅ 한글/숫자 깨짐 방지: OS별 폰트 지정
try:
    plt.rcParams["font.family"] = "Malgun Gothic"   # Windows
except Exception:
    for cand in ["AppleGothic", "NanumGothic", "DejaVu Sans"]:
        try:
            plt.rcParams["font.family"] = cand
            break
        except Exception:
            pass
mpl.rcParams["axes.unicode_minus"] = False

# tkcalendar (없으면 자동 폴백)
try:
    from tkcalendar import Calendar
    HAVE_TKCALENDAR = True
except Exception:
    HAVE_TKCALENDAR = False

from services import storage, analytics
from services.auth import get_current_user
from app.config import COLOR_BORDER, COLOR_PANEL
from ui.components.topbar import TopBar


class AnalyticsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # 상단바
        self.topbar = TopBar(self, app, title="분석", show_back=True, back_to="home")
        self.topbar.pack(fill="x")

        # 콘텐츠 영역
        content = ttk.Frame(self, style="Page.TFrame")
        content.pack(fill="both", expand=True)

        # 컨트롤 패널
        panel = tk.Frame(
            content, bg=COLOR_PANEL, highlightthickness=1,
            highlightbackground=COLOR_BORDER, padx=10, pady=8
        )
        panel.pack(fill="x")

        ttk.Label(panel, text="월(YYYY-MM)").grid(row=0, column=0, sticky="e")
        self.ent_month = ttk.Entry(panel, width=10)
        self.ent_month.grid(row=0, column=1, padx=(6, 8))
        self.ent_month.insert(0, datetime.now().strftime("%Y-%m"))

        btn_col_start = 2
        if HAVE_TKCALENDAR:
            ttk.Button(panel, text="📅", width=3, command=self._pick_month)\
                .grid(row=0, column=2, padx=4)
            btn_col_start = 3

        ttk.Button(panel, text="카테고리 막대", command=self._bar)\
            .grid(row=0, column=btn_col_start + 0, padx=4)
        ttk.Button(panel, text="일자 순증감", command=self._line)\
            .grid(row=0, column=btn_col_start + 1, padx=4)
        ttk.Button(panel, text="수입/지출 파이", command=self._pie)\
            .grid(row=0, column=btn_col_start + 2, padx=4)

        self.info = ttk.Label(content, text="월을 입력하거나 📅 버튼으로 선택한 뒤, 원하는 그래프 버튼을 클릭하세요.", anchor="w")
        self.info.pack(fill="x", pady=(10, 0))

    def on_show(self):
        self.topbar.refresh_user()

    @property
    def _csv_path(self):
        from services.storage import csv_path_for_user
        u = get_current_user()
        return csv_path_for_user(u.username)

    def _get_summary(self):
        month = self.ent_month.get().strip()
        if not self._is_valid_month(month):
            messagebox.showwarning("형식", "월 형식은 YYYY-MM 입니다. 예) 2025-08")
            return None, None, None
        df = storage.read_all(self._csv_path)
        summary = analytics.month_summary(df, month)
        return month, df, summary

    @staticmethod
    def _is_valid_month(s: str) -> bool:
        try:
            datetime.strptime(s, "%Y-%m")
            return True
        except Exception:
            return False

    # ---------- 그래프 액션 ----------
    def _bar(self):
        month, df, summary = self._get_summary()
        if month is None:
            return
        if summary.empty:
            messagebox.showinfo("안내", f"{month} 데이터가 없습니다.")
            return
        plt.figure()
        plt.title(f"{month} 카테고리별 수입/지출")
        x = range(len(summary))
        plt.bar(x, summary["수입"], label="수입", linewidth=0)
        plt.bar(x, -summary["지출"], label="지출", linewidth=0)
        plt.xticks(x, summary["category"], rotation=30)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def _line(self):
        month, df, summary = self._get_summary()
        if month is None:
            return
        ser = analytics.daily_net_series(df, month)
        if ser.size == 0:
            messagebox.showinfo("안내", f"{month} 데이터가 없습니다.")
            return

        # ✅ x축을 날짜로 처리하고 '일(01~31)' 숫자만 보이게 포맷
        x_dt = pd.to_datetime(ser.index)              # 문자열 → datetime
        y = ser.values

        fig = plt.figure()
        plt.title(f"{month} 일자별 순증감(수입-지출)")
        plt.plot(x_dt, y, marker="o")

        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d"))  # 01, 02, ... 형태
        ax.xaxis.set_major_locator(mdates.DayLocator())           # 일 단위 눈금
        plt.xticks(rotation=0)                                    # 숫자라 회전 불필요
        plt.tight_layout()
        plt.show()

    def _pie(self):
        month, df, summary = self._get_summary()
        if month is None:
            return
        if summary.empty:
            messagebox.showinfo("안내", f"{month} 데이터가 없습니다.")
            return
        total_inc = float(summary["수입"].sum())
        total_exp = float(summary["지출"].sum())
        plt.figure()
        plt.title(f"{month} 수입/지출 비중")
        plt.pie([total_inc, total_exp], labels=["수입", "지출"], autopct="%.1f%%", startangle=90)
        plt.axis("equal")
        plt.show()

    # ---------- 달력 팝업 ----------
    def _pick_month(self):
        top = tk.Toplevel(self)
        top.title("월 선택")
        top.transient(self.winfo_toplevel())
        top.grab_set()

        today = datetime.today()
        cal = Calendar(top, selectmode="day", year=today.year, month=today.month, day=today.day)
        cal.pack(padx=10, pady=10)

        def _ok():
            try:
                sel = cal.selection_get()
                y, m = sel.year, sel.month
                self.ent_month.delete(0, "end")
                self.ent_month.insert(0, f"{y:04d}-{m:02d}")
            except Exception:
                pass
            finally:
                top.destroy()

        btns = ttk.Frame(top)
        btns.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(btns, text="확인", command=_ok).pack(side="right")
        ttk.Button(btns, text="취소", command=top.destroy).pack(side="right", padx=(0, 6))
