import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pandas as pd

from ui.components.topbar import TopBar
from services.auth import get_current_user
from services import storage, analytics

# (선택) 아바타 표시를 위한 Pillow
try:
    from PIL import Image, ImageTk  # type: ignore
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False


class HomeFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # 상단 프로필/로그아웃 바
        self.topbar = TopBar(self, app, title="오늘의 마침표")
        self.topbar.pack(fill="x")

        # 상단 네비 (우측 정렬: 가계부 / 분석 / 프로필 변경)
        nav = ttk.Frame(self, padding=(16, 8))
        nav.pack(fill="x")
        ttk.Label(nav, text="").pack(side="left", expand=True)  # 오른쪽 정렬용 스페이서
        ttk.Button(nav, text="가계부", command=lambda: self.app.show("account")).pack(side="right", padx=4)
        ttk.Button(nav, text="분석", command=lambda: self.app.show("analytics")).pack(side="right", padx=4)
        ttk.Button(nav, text="프로필 변경", command=self._profile_settings).pack(side="right", padx=4)

        # 메인 그리드
        page = ttk.Frame(self, padding=(16, 8))
        page.pack(fill="both", expand=True)
        page.grid_columnconfigure(0, weight=3)  # 왼쪽 컬럼 넓게
        page.grid_columnconfigure(1, weight=2)
        page.grid_rowconfigure(0, weight=2)
        page.grid_rowconfigure(1, weight=2)

        # --- 카드 1: 이번달 카테고리 요약(그래프)
        self.card_chart = self._make_card(page, "이번달 카테고리 요약", row=0, col=0, padx=(0, 12), pady=(0, 12))
        self.chart_body = ttk.Frame(self.card_chart["body"])
        self.chart_body.pack(fill="both", expand=True)
        self._chart_canvas = None  # FigureCanvasTkAgg 참조

        # --- 카드 2: 프로필 카드 (플레이스홀더로 생성 → on_show에서 채움)
        self.card_profile = self._make_card(page, "프로필", row=0, col=1, padx=(12, 0), pady=(0, 12))
        self._build_profile(self.card_profile["body"])  # 내부 라벨만 만들어둠

        # --- 카드 3: 최근 7일 요약
        self.card_week = self._make_card(page, "최근 7일 요약", row=1, col=0, padx=(0, 12), pady=(12, 0))
        self.week_body = ttk.Frame(self.card_week["body"])
        self.week_body.pack(fill="both", expand=True)
        self._week_items = []

        # --- 카드 4: 빠른 기록
        self.card_quick = self._make_card(page, "빠른 기록", row=1, col=1, padx=(12, 0), pady=(12, 0))
        self._build_quick_entry(self.card_quick["body"])

        # 아바타 이미지 참조(가비지 컬렉션 방지)
        self._avatar_img = None

    def on_show(self):
        # 화면 보여질 때마다 사용자/데이터 갱신
        self.topbar.refresh_user()
        self._update_profile_card()     # ✅ 여기서 실제 사용자 정보를 채움
        self._render_month_chart()
        self._render_week_summary()

    # -------------------- 카드 공용 --------------------
    def _make_card(self, parent, title, *, row, col, padx=6, pady=6):
        """카드 스타일: 패널 + 내부 바디 프레임 반환"""
        outer = tk.Frame(
            parent, bg="white",
            highlightthickness=1, highlightbackground="#e5e7eb"
        )
        outer.grid(row=row, column=col, sticky="nsew", padx=padx, pady=pady)
        parent.grid_rowconfigure(row, weight=1)

        # 제목
        hdr = ttk.Frame(outer)
        hdr.pack(fill="x", padx=16, pady=(14, 8))
        ttk.Label(hdr, text=title, font=("Malgun Gothic", 11, "bold")).pack(side="left")

        # 가는 구분선
        sep = ttk.Separator(outer, orient="horizontal")
        sep.pack(fill="x", padx=16)

        # 바디
        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True, padx=16, pady=16)
        return {"frame": outer, "body": body}

    # -------------------- 카드 2: 프로필 --------------------
    def _build_profile(self, parent):
        """라벨만 만들어두고 값은 on_show()에서 채움 (로그인 전 None 대응)"""
        row = ttk.Frame(parent)
        row.pack(fill="x")

        # 아바타(왼쪽)
        self.lbl_avatar = ttk.Label(row)
        self.lbl_avatar.pack(side="left", padx=(0, 12))

        # 텍스트 정보(오른쪽)
        right = ttk.Frame(row)
        right.pack(side="left", fill="x", expand=True)

        self.lbl_profile_name = ttk.Label(right, text="—", font=("Malgun Gothic", 22, "bold"))
        self.lbl_profile_name.pack(pady=(0, 6), anchor="w")

        self.lbl_profile_id = ttk.Label(right, text="회원 ID : -")
        self.lbl_profile_id.pack(anchor="w", pady=2)
        self.lbl_profile_join = ttk.Label(right, text="가입일 : -")
        self.lbl_profile_join.pack(anchor="w", pady=2)

        ttk.Button(parent, text="프로필 설정", command=self._profile_settings).pack(pady=(12, 0), anchor="e")

    def _update_profile_card(self):
        """로그인 후 사용자 정보로 프로필 카드 채우기 (None 안전)"""
        u = get_current_user()
        if not u:
            self.lbl_profile_name.config(text="—")
            self.lbl_profile_id.config(text="회원 ID : -")
            self.lbl_profile_join.config(text="가입일 : -")
            self.lbl_avatar.config(image="", text="(아바타 없음)")
            return

        self.lbl_profile_name.config(text=u.display_name)
        self.lbl_profile_id.config(text=f"회원 ID : {u.username}")
        self.lbl_profile_join.config(text=f"가입일 : {self._guess_join_date(u.username)}")

        # 아바타 로드
        if getattr(u, "avatar", None) and HAVE_PIL:
            try:
                im = Image.open(u.avatar)
                im.thumbnail((96, 96))
                self._avatar_img = ImageTk.PhotoImage(im)
                self.lbl_avatar.config(image=self._avatar_img, text="")
            except Exception:
                self.lbl_avatar.config(image="", text="(이미지 오류)")
        else:
            self.lbl_avatar.config(image="", text="(아바타 없음)")

    def _guess_join_date(self, username: str) -> str:
        """사용자 CSV 파일 생성일을 가입일로 추정 (없으면 오늘)"""
        csv_path = storage.csv_path_for_user(username)
        if csv_path.exists():
            try:
                ts = csv_path.stat().st_ctime
                return datetime.fromtimestamp(ts).strftime("%Y. %m. %d.")
            except Exception:
                pass
        return datetime.today().strftime("%Y. %m. %d.")

    def _profile_settings(self):
        # 프로필 설정 모달 열기 → 닫히면 홈 새로고침
        try:
            from ui.pages.profile_settings import ProfileDialog
        except Exception:
            messagebox.showwarning("안내", "프로필 설정 화면을 찾을 수 없습니다.")
            return
        dlg = ProfileDialog(self)
        self.wait_window(dlg)
        # 저장 후 상단바/프로필 카드/차트 다시 갱신
        self.topbar.refresh_user()
        self._update_profile_card()
        self._render_month_chart()

    # -------------------- 카드 1: 이번달 차트 --------------------
    def _render_month_chart(self):
        # 캔버스 초기화
        if self._chart_canvas is not None:
            self._chart_canvas.get_tk_widget().destroy()
            self._chart_canvas = None

        u = get_current_user()
        if not u:
            fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
            ax.text(0.5, 0.5, "로그인 정보가 없습니다.", ha="center", va="center")
            ax.set_axis_off()
            fig.tight_layout()
            self._chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_body)
            self._chart_canvas.draw()
            self._chart_canvas.get_tk_widget().pack(fill="both", expand=True)
            return

        df = storage.read_all(storage.csv_path_for_user(u.username))
        month = datetime.now().strftime("%Y-%m")
        summary = analytics.month_summary(df, month)

        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
        if summary.empty:
            ax.text(0.5, 0.5, f"{month} 데이터가 없습니다.", ha="center", va="center")
            ax.set_axis_off()
        else:
            # Top5 카테고리만 (수입+지출 절대값 기준)
            summary = summary.copy()
            summary["총액절대"] = (summary["수입"].abs() + summary["지출"].abs())
            summary = summary.sort_values("총액절대", ascending=False).head(5)
            x = range(len(summary))
            ax.bar(x, summary["수입"], label="수입", linewidth=0)
            ax.bar(x, -summary["지출"], label="지출", linewidth=0)
            ax.set_xticks(list(x))
            ax.set_xticklabels(summary["category"], rotation=0)
            ax.legend(loc="upper right")
            ax.set_ylabel("금액")
            ax.set_title(f"{month} Top 5 카테고리")

        fig.tight_layout()
        self._chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_body)
        self._chart_canvas.draw()
        self._chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    # -------------------- 카드 3: 최근 7일 요약 --------------------
    def _render_week_summary(self):
        # 기존 아이템 제거
        for w in self._week_items:
            w.destroy()
        self._week_items.clear()

        u = get_current_user()
        if not u:
            return

        df = storage.read_all(storage.csv_path_for_user(u.username))
        if df.empty or "date" not in df.columns:
            dates = [datetime.today() - timedelta(days=i) for i in range(6, -1, -1)]
            self._draw_week_chips(dates, {})
            return

        # 최근 7일 날짜 리스트 (과거->오늘 순)
        dates = [datetime.today() - timedelta(days=i) for i in range(6, -1, -1)]

        # 날짜별 순증감 계산
        df2 = df.copy()
        df2["amount"] = pd.to_numeric(df2["amount"], errors="coerce").fillna(0).astype(int)
        df2["signed"] = df2.apply(lambda r: r["amount"] if r["type"] == "수입" else -r["amount"], axis=1)
        daily = df2.groupby("date")["signed"].sum().to_dict()  # {'YYYY-MM-DD': net}

        self._draw_week_chips(dates, daily)

    def _draw_week_chips(self, dates, daily_map):
        wrap = self.card_week["body"]

        # 이전 내용 비우기
        for child in wrap.winfo_children():
            child.destroy()

        legend = ttk.Label(wrap, text="· 값은 (수입-지출) 순증감입니다. 음수면 지출이 더 큼", foreground="#6b7280")
        legend.pack(anchor="w", pady=(0, 8))

        grid = ttk.Frame(wrap)
        grid.pack()

        for i, d in enumerate(dates):
            # 칩 프레임
            chip = tk.Frame(
                grid, bg="white",
                highlightthickness=1, highlightbackground="#e5e7eb"
            )
            chip.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
            self._week_items.append(chip)

            # 상단: 요일/일자
            ttk.Label(chip, text=d.strftime("%a"), foreground="#6b7280").pack(pady=(10, 2))
            circle = tk.Canvas(chip, width=64, height=64, highlightthickness=0, bg="white")
            circle.pack()
            circle.create_oval(6, 6, 58, 58, outline="#c7d2fe", width=2)
            circle.create_text(32, 32, text=d.strftime("%d"), fill="#374151")

            # 값
            net = int(daily_map.get(d.strftime("%Y-%m-%d"), 0))
            val = f"{net:+,}"
            ttk.Label(chip, text=val, font=("Malgun Gothic", 10, "bold")).pack(pady=(6, 10))

        # 그리드 늘어나게
        for i in range(len(dates)):
            grid.grid_columnconfigure(i, weight=1)

    # -------------------- 카드 4: 빠른 기록 --------------------
    def _build_quick_entry(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(0, 8))

        ttk.Label(row, text="구분").pack(side="left")
        self.q_type = ttk.Combobox(row, values=["지출", "수입"], width=6, state="readonly")
        self.q_type.set("지출"); self.q_type.pack(side="left", padx=(6, 12))

        ttk.Label(row, text="금액").pack(side="left")
        self.q_amt = ttk.Entry(row, width=12)
        self.q_amt.pack(side="left", padx=(6, 12))

        ttk.Label(row, text="설명").pack(side="left")
        self.q_desc = ttk.Entry(row, width=28)
        self.q_desc.pack(side="left", padx=(6, 12))

        ttk.Button(parent, text="저장", command=self._quick_save).pack(anchor="e")

        help_ = ttk.Label(parent, text="* 오늘 날짜로 저장됩니다. 자세한 입력은 가계부 화면을 이용하세요.", foreground="#6b7280")
        help_.pack(anchor="w", pady=(8, 0))

    def _quick_save(self):
        try:
            amt = int(self.q_amt.get().replace(",", "").strip())
            desc = self.q_desc.get().strip() or "빠른기록"
            typ = self.q_type.get()
        except Exception:
            messagebox.showwarning("입력", "금액을 숫자로 입력하세요.")
            return

        u = get_current_user()
        if not u:
            messagebox.showwarning("로그인", "로그인 후 이용해주세요.")
            return

        path = storage.csv_path_for_user(u.username)
        row = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": typ,
            "category": "기타",
            "description": desc,
            "amount": amt,
        }
        storage.append_row(row, path)
        messagebox.showinfo("저장", "빠른 기록이 저장되었습니다.")
        self._render_month_chart()
        self._render_week_summary()
