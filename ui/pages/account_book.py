import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# tkcalendar (없으면 자동 폴백)
try:
    from tkcalendar import DateEntry, Calendar
    HAVE_TKCALENDAR = True
except Exception:
    HAVE_TKCALENDAR = False

from app.config import (
    CATEGORIES, DATE_FMT,
    COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_ACCENT,
    COLOR_INC, COLOR_EXP, COLOR_STRIPE
)
from models.transaction import Transaction
from services import analytics, storage
from services.auth import get_current_user
from ui.components.topbar import TopBar


def _comma(n: int) -> str:
    return f"{int(n):,}"


class AccountBookPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.topbar = TopBar(self, app, title="가계부", show_back=True, back_to="home")
        self.topbar.pack(fill="x")

        content = ttk.Frame(self, style="Page.TFrame")
        content.pack(fill="both", expand=True)

        self._build_toolbar(content)
        self._build_table(content)
        self._build_bottom(content)

    def on_show(self):
        self.topbar.refresh_user()
        self._load_data()

    # ---------- UI ----------
    def _build_toolbar(self, parent):
        bar = ttk.Frame(parent)
        bar.pack(fill="x")

        panel = tk.Frame(
            bar, bg=COLOR_PANEL, highlightthickness=1,
            highlightbackground=COLOR_BORDER, padx=10, pady=8
        )
        panel.pack(fill="x")

        # 날짜
        ttk.Label(panel, text="날짜").grid(row=0, column=0, sticky="w")
        if HAVE_TKCALENDAR:
            self.ent_date = DateEntry(
                panel, width=12, date_pattern="yyyy-mm-dd"
            )
            self.ent_date.grid(row=1, column=0, padx=(0, 8))
            # 날짜 선택 시 월 입력칸 동기화 (예: 2025-08)
            self.ent_date.bind("<<DateEntrySelected>>", lambda e: self._sync_month_from_date())
        else:
            self.ent_date = ttk.Entry(panel, width=12)
            self.ent_date.grid(row=1, column=0, padx=(0, 8))
            self.ent_date.insert(0, datetime.now().strftime(DATE_FMT))

        # 구분
        ttk.Label(panel, text="구분").grid(row=0, column=1, sticky="w")
        self.cmb_type = ttk.Combobox(panel, values=["지출", "수입"], width=7, state="readonly")
        self.cmb_type.grid(row=1, column=1, padx=(0, 8))
        self.cmb_type.set("지출")

        # 카테고리
        ttk.Label(panel, text="카테고리").grid(row=0, column=2, sticky="w")
        self.cmb_cat = ttk.Combobox(panel, values=CATEGORIES, width=14, state="readonly")
        self.cmb_cat.grid(row=1, column=2, padx=(0, 8))
        self.cmb_cat.set(CATEGORIES[0])

        # 설명
        ttk.Label(panel, text="설명").grid(row=0, column=3, sticky="w")
        self.ent_desc = ttk.Entry(panel, width=38)
        self.ent_desc.grid(row=1, column=3, padx=(0, 8))

        # 금액
        ttk.Label(panel, text="금액(원)").grid(row=0, column=4, sticky="w")
        self.ent_amt = ttk.Entry(panel, width=14)
        self.ent_amt.grid(row=1, column=4, padx=(0, 16))

        # 버튼 스타일
        style_btn = ttk.Style(panel)
        style_btn.configure("Accent.TButton", foreground="white", background=COLOR_ACCENT)
        try:
            style_btn.map("Accent.TButton", background=[("active", COLOR_ACCENT)])
        except Exception:
            pass

        # 기능 버튼들
        ttk.Button(panel, text="추가", style="Accent.TButton", command=self._on_add)\
            .grid(row=1, column=5, padx=6)
        ttk.Button(panel, text="선택 삭제", command=self._on_delete)\
            .grid(row=1, column=6, padx=6)
        ttk.Button(panel, text="홈으로", command=lambda: self.app.show("home"))\
            .grid(row=1, column=7, padx=6)

        # 월(YYYY-MM) + 달력 버튼 + 그래프
        ttk.Label(panel, text="월(YYYY-MM)").grid(row=0, column=8, sticky="w")
        self.ent_month = ttk.Entry(panel, width=10)
        self.ent_month.grid(row=1, column=8, padx=(0, 6))
        self.ent_month.insert(0, datetime.now().strftime("%Y-%m"))

        if HAVE_TKCALENDAR:
            # 📅 버튼으로 팝업 달력에서 월 선택
            ttk.Button(panel, text="📅", width=3, command=self._pick_month)\
                .grid(row=1, column=9, padx=(0, 6))
            col_for_chart = 10
        else:
            col_for_chart = 9

        ttk.Button(panel, text="월별 그래프", command=self._on_chart)\
            .grid(row=1, column=col_for_chart, padx=(0, 0))

        # 열 간격: 최대 0~10까지
        for c in range(11):
            panel.grid_columnconfigure(c, pad=2)

    def _build_table(self, parent):
        body = ttk.Frame(parent)
        body.pack(fill="both", expand=True, pady=(10, 0))

        cols = ("date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", height=18)
        headings = ["날짜", "구분", "카테고리", "설명", "금액"]
        widths = [110, 70, 140, 520, 110]
        anchors = ["center", "center", "center", "w", "e"]

        for c, label, w, a in zip(cols, headings, widths, anchors):
            self.tree.heading(c, text=label)
            self.tree.column(c, width=w, anchor=a, stretch=(c == "description"))

        vsb = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("odd", background=COLOR_STRIPE)
        self.tree.tag_configure("inc", foreground=COLOR_INC)
        self.tree.tag_configure("exp", foreground=COLOR_EXP)

    def _build_bottom(self, parent):
        bottom = tk.Frame(parent, bg=COLOR_BG)
        bottom.pack(fill="x", pady=6)
        self.lbl_summary = ttk.Label(bottom, text="합계: 0원 (수입 0원 / 지출 0원)")
        self.lbl_summary.pack(anchor="e")

    # ---------- 동작 ----------
    @property
    def _csv_path(self):
        from services.storage import csv_path_for_user
        u = get_current_user()
        return csv_path_for_user(u.username)

    def _load_data(self):
        try:
            df = storage.read_all(self._csv_path)
        except Exception as e:
            messagebox.showerror("오류", f"CSV 읽기 실패: {e}")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        inc = exp = 0
        for idx, row in df.iterrows():
            amt = int(row["amount"]) if str(row["amount"]).strip() else 0
            tags = []
            tags.append("odd" if idx % 2 else "")
            if row["type"] == "수입":
                tags.append("inc"); inc += amt
            else:
                tags.append("exp"); exp += amt

            self.tree.insert(
                "", "end",
                values=(row["date"], row["type"], row["category"], row["description"], _comma(amt)),
                tags=tuple(t for t in tags if t)
            )

        total = inc - exp
        self.lbl_summary.config(text=f"합계: {_comma(total)}원 (수입 {_comma(inc)}원 / 지출 {_comma(exp)}원)")

    def _on_add(self):
        try:
            amt = int(self.ent_amt.get().replace(",", "").strip())
            tx = Transaction(
                date=self.ent_date.get().strip(),
                type=self.cmb_type.get().strip(),
                category=self.cmb_cat.get().strip(),
                description=self.ent_desc.get().strip(),
                amount=amt,
            )
            Transaction.validate(tx)
        except Exception as e:
            messagebox.showwarning("입력 오류", f"잘못된 값: {e}")
            return

        storage.append_row(tx.__dict__, self._csv_path)
        self._load_data()
        self.ent_desc.delete(0, "end")
        self.ent_amt.delete(0, "end")

    def _on_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("안내", "삭제할 항목을 선택하세요.")
            return

        all_items = list(self.tree.get_children())
        keep_values = []
        for item in all_items:
            if item in sel:
                continue
            vals = list(self.tree.item(item)["values"])
            vals[4] = int(str(vals[4]).replace(",", ""))
            keep_values.append(vals)

        import pandas as pd
        df = pd.DataFrame(keep_values, columns=["date", "type", "category", "description", "amount"])
        if not df.empty:
            df["amount"] = df["amount"].astype(int)
        storage.overwrite(df, self._csv_path)
        self._load_data()

    def _on_chart(self):
        month = self.ent_month.get().strip()
        df = storage.read_all(self._csv_path)
        summary = analytics.month_summary(df, month)
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

    # ---------- 달력 유틸 ----------
    def _sync_month_from_date(self):
        """DateEntry에서 날짜를 선택하면 ent_month를 해당 'YYYY-MM'으로 동기화"""
        try:
            d = self.ent_date.get().strip()  # 'yyyy-mm-dd'
            self.ent_month.delete(0, "end")
            self.ent_month.insert(0, d[:7])  # 'yyyy-mm'
        except Exception:
            pass

    def _pick_month(self):
        """팝업 달력에서 임의 날짜를 선택 -> 해당 달(YYYY-MM)을 ent_month에 반영"""
        top = tk.Toplevel(self)
        top.title("월 선택")
        top.transient(self.winfo_toplevel())
        top.grab_set()

        today = datetime.today()
        cal = Calendar(top, selectmode="day", year=today.year, month=today.month, day=today.day)
        cal.pack(padx=10, pady=10)

        def _ok():
            try:
                sel = cal.selection_get()  # datetime.date
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
