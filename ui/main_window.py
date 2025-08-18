import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from app.config import CATEGORIES, DATE_FMT, CSV_PATH
from models.transaction import Transaction
from services import storage, analytics

class MainWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._build_toolbar()
        self._build_table()
        self._load_data()

    # ---------- UI ----------
    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=12, pady=8)

        # 날짜
        ttk.Label(bar, text="날짜").grid(row=0, column=0)
        self.ent_date = ttk.Entry(bar, width=12)
        self.ent_date.grid(row=1, column=0, padx=4)
        self.ent_date.insert(0, datetime.now().strftime(DATE_FMT))

        # 수입/지출
        ttk.Label(bar, text="구분").grid(row=0, column=1)
        self.cmb_type = ttk.Combobox(bar, values=["수입", "지출"], width=6, state="readonly")
        self.cmb_type.grid(row=1, column=1, padx=4)
        self.cmb_type.set("지출")

        # 카테고리
        ttk.Label(bar, text="카테고리").grid(row=0, column=2)
        self.cmb_cat = ttk.Combobox(bar, values=CATEGORIES, width=12, state="readonly")
        self.cmb_cat.grid(row=1, column=2, padx=4)
        self.cmb_cat.set(CATEGORIES[0])

        # 설명
        ttk.Label(bar, text="설명").grid(row=0, column=3)
        self.ent_desc = ttk.Entry(bar, width=30)
        self.ent_desc.grid(row=1, column=3, padx=4)

        # 금액
        ttk.Label(bar, text="금액(원)").grid(row=0, column=4)
        self.ent_amt = ttk.Entry(bar, width=12)
        self.ent_amt.grid(row=1, column=4, padx=4)

        # 버튼들
        btn_add = ttk.Button(bar, text="추가", command=self._on_add)
        btn_add.grid(row=1, column=5, padx=6)

        btn_del = ttk.Button(bar, text="선택 삭제", command=self._on_delete)
        btn_del.grid(row=1, column=6, padx=6)

        btn_save = ttk.Button(bar, text="저장(CSV)", command=self._on_save)
        btn_save.grid(row=1, column=7, padx=6)

        btn_reload = ttk.Button(bar, text="새로고침", command=self._load_data)
        btn_reload.grid(row=1, column=8, padx=6)

        # 월 선택/그래프
        ttk.Label(bar, text="월(YYYY-MM)").grid(row=0, column=9)
        self.ent_month = ttk.Entry(bar, width=8)
        self.ent_month.grid(row=1, column=9, padx=4)
        self.ent_month.insert(0, datetime.now().strftime("%Y-%m"))

        btn_chart = ttk.Button(bar, text="월별 그래프", command=self._on_chart)
        btn_chart.grid(row=1, column=10, padx=6)

    def _build_table(self):
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        cols = ("date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", height=18)
        for c, label, w in zip(cols, ["날짜", "구분", "카테고리", "설명", "금액"], [100, 60, 120, 380, 100]):
            self.tree.heading(c, text=label)
            self.tree.column(c, width=w, anchor="center" if c != "description" else "w")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        # 합계 표시
        self.lbl_summary = ttk.Label(self, text="합계: 0원 (수입 0원 / 지출 0원)")
        self.lbl_summary.pack(anchor="e", padx=16, pady=4)

    # ---------- 동작 ----------
    def _load_data(self):
        try:
            df = storage.read_all(CSV_PATH)
        except Exception as e:
            messagebox.showerror("오류", f"CSV 읽기 실패: {e}")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        inc = exp = 0
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=tuple(row[c] for c in ("date", "type", "category", "description", "amount")))
            if row["type"] == "수입":
                inc += int(row["amount"])
            else:
                exp += int(row["amount"])
        total = inc - exp
        self.lbl_summary.config(text=f"합계: {total:,}원 (수입 {inc:,}원 / 지출 {exp:,}원)")

    def _on_add(self):
        try:
            tx = Transaction(
                date=self.ent_date.get().strip(),
                type=self.cmb_type.get().strip(),
                category=self.cmb_cat.get().strip(),
                description=self.ent_desc.get().strip(),
                amount=int(self.ent_amt.get().replace(",", "").strip()),
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
        # Tree에서 선택 삭제 후 CSV로 반영
        all_rows = [self.tree.item(i)["values"] for i in self.tree.get_children()]
        keep = [v for i, v in enumerate(all_rows) if self.tree.get_children()[i] not in sel]
        import pandas as pd
        df = pd.DataFrame(keep, columns=["date", "type", "category", "description", "amount"])
        df["amount"] = df["amount"].astype(int)
        storage.overwrite(df)
        self._load_data()

    def _on_save(self):
        try:
            # 이미 append/overwrite가 즉시 CSV에 쓰고 있지만, 수동 저장 동작도 제공
            messagebox.showinfo("저장", f"CSV 저장 경로:\n{CSV_PATH}")
        except Exception as e:
            messagebox.showerror("오류", str(e))

    def _on_chart(self):
        month = self.ent_month.get().strip()
        df = storage.read_all(CSV_PATH)

        # 1) 카테고리별 수입/지출 막대
        summary = analytics.month_summary(df, month)
        if summary.empty:
            messagebox.showinfo("안내", f"{month} 데이터가 없습니다.")
            return

        plt.figure()
        plt.title(f"{month} 카테고리별 수입/지출")
        x = range(len(summary))
        plt.bar(x, summary["수입"], label="수입")
        plt.bar(x, -summary["지출"], label="지출")
        plt.xticks(x, summary["category"], rotation=30)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # 2) 일자별 순증감 선그래프
        ser = analytics.daily_net_series(df, month)
        if not ser.empty:
            plt.figure()
            plt.title(f"{month} 일자별 순증감(수입-지출)")
            plt.plot(list(ser.index), list(ser.values), marker="o")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
