import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from app.config import (
    CATEGORIES, DATE_FMT, CSV_PATH,
    COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_ACCENT,
    COLOR_INC, COLOR_EXP, COLOR_STRIPE
)
from models.transaction import Transaction
from services import storage, analytics

def _comma(n: int) -> str:
    return f"{int(n):,}"

class MainWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)
        self._build_toolbar()
        self._build_table()
        self._load_data()

    # ---------- UI ----------
    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x")

        # 내부 패널(약간 배경 차이 및 보더)
        panel = tk.Frame(
            bar, bg=COLOR_PANEL, highlightthickness=1,
            highlightbackground=COLOR_BORDER, padx=10, pady=8
        )
        panel.pack(fill="x")

        # 날짜
        ttk.Label(panel, text="날짜").grid(row=0, column=0, sticky="w")
        self.ent_date = ttk.Entry(panel, width=12)
        self.ent_date.grid(row=1, column=0, padx=(0, 8))
        self.ent_date.insert(0, datetime.now().strftime(DATE_FMT))

        # 수입/지출
        ttk.Label(panel, text="구분").grid(row=0, column=1, sticky="w")
        self.cmb_type = ttk.Combobox(panel, values=["수입", "지출"], width=7, state="readonly")
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

        # 버튼들 (강조색)
        style_btn = ttk.Style(panel)
        style_btn.configure("Accent.TButton", foreground="white", background=COLOR_ACCENT)
        try:
            style_btn.map("Accent.TButton", background=[("active", COLOR_ACCENT)])
        except Exception:
            pass

        ttk.Button(panel, text="추가", style="Accent.TButton", command=self._on_add)\
            .grid(row=1, column=5, padx=6)
        ttk.Button(panel, text="선택 삭제", command=self._on_delete)\
            .grid(row=1, column=6, padx=6)
        ttk.Button(panel, text="저장(CSV)", command=self._on_save)\
            .grid(row=1, column=7, padx=6)

        # 월 선택/그래프
        ttk.Label(panel, text="월(YYYY-MM)").grid(row=0, column=8, sticky="w")
        self.ent_month = ttk.Entry(panel, width=10)
        self.ent_month.grid(row=1, column=8, padx=(0, 6))
        self.ent_month.insert(0, datetime.now().strftime("%Y-%m"))
        ttk.Button(panel, text="월별 그래프", command=self._on_chart)\
            .grid(row=1, column=9, padx=(0, 0))

        # 그리드 여백
        for c in range(10):
            panel.grid_columnconfigure(c, pad=2)

    def _build_table(self):
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=(10, 0))

        cols = ("date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", height=18)
        headings = ["날짜", "구분", "카테고리", "설명", "금액"]
        widths = [110, 70, 140, 520, 110]
        anchors = ["center", "center", "center", "w", "e"]

        for c, label, w, a in zip(cols, headings, widths, anchors):
            self.tree.heading(c, text=label)
            self.tree.column(c, width=w, anchor=a, stretch=(c == "description"))

        # 스크롤바
        vsb = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # 줄무늬/색상 태그
        self.tree.tag_configure("odd", background=COLOR_STRIPE)
        self.tree.tag_configure("inc", foreground=COLOR_INC)
        self.tree.tag_configure("exp", foreground=COLOR_EXP)

        # 합계 표시 패널
        bottom = tk.Frame(self, bg=COLOR_BG)
        bottom.pack(fill="x", pady=6)
        self.lbl_summary = ttk.Label(bottom, text="합계: 0원 (수입 0원 / 지출 0원)")
        self.lbl_summary.pack(anchor="e")

    # ---------- 동작 ----------
    def _load_data(self):
        try:
            df = storage.read_all(CSV_PATH)
        except Exception as e:
            messagebox.showerror("오류", f"CSV 읽기 실패: {e}")
            return

        # 테이블 비우기
        for i in self.tree.get_children():
            self.tree.delete(i)

        inc = exp = 0
        for idx, row in df.iterrows():
            amt = int(row["amount"])
            tags = []
            tags.append("odd" if idx % 2 else "")
            if row["type"] == "수입":
                tags.append("inc")
                inc += amt
            else:
                tags.append("exp")
                exp += amt

            values = (
                row["date"], row["type"], row["category"],
                row["description"], _comma(amt)  # 3자리 콤마 형식 표시
            )
            self.tree.insert("", "end", values=values, tags=tuple(t for t in tags if t))

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

        storage.append_row(tx.__dict__)
        self._load_data()
        self.ent_desc.delete(0, "end")
        self.ent_amt.delete(0, "end")

    def _on_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("안내", "삭제할 항목을 선택하세요.")
            return

        # 현재 테이블의 모든 행을 가져와서 선택된 행을 제외하고 CSV로 덮어쓰기
        all_items = list(self.tree.get_children())
        keep_values = []
        for i, item in enumerate(all_items):
            if item in sel:
                continue
            vals = self.tree.item(item)["values"]
            # amount는 화면표시가 "1,234" 이므로 콤마 제거
            vals = list(vals)
            vals[4] = int(str(vals[4]).replace(",", ""))
            keep_values.append(vals)

        import pandas as pd
        df = pd.DataFrame(keep_values, columns=["date", "type", "category", "description", "amount"])
        if not df.empty:
            df["amount"] = df["amount"].astype(int)
        storage.overwrite(df)
        self._load_data()

    def _on_save(self):
        try:
            messagebox.showinfo("저장", f"CSV 저장 경로:\n{CSV_PATH}")
        except Exception as e:
            messagebox.showerror("오류", str(e))

    def _on_chart(self):
        month = self.ent_month.get().strip()
        df = storage.read_all(CSV_PATH)

        summary = analytics.month_summary(df, month)
        if summary.empty:
            messagebox.showinfo("안내", f"{month} 데이터가 없습니다.")
            return

        # 1) 카테고리별 수입/지출 막대
        plt.figure()
        plt.title(f"{month} 카테고리별 수입/지출")
        x = range(len(summary))
        plt.bar(x, summary["수입"], label="수입", linewidth=0)
        plt.bar(x, -summary["지출"], label="지출", linewidth=0)
        plt.xticks(x, summary["category"], rotation=30)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # 2) 일자별 순증감 선그래프
        ser = analytics.daily_net_series(df, month)
        if ser.size > 0:
            plt.figure()
            plt.title(f"{month} 일자별 순증감(수입-지출)")
            plt.plot(list(ser.index), list(ser.values), marker="o")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
