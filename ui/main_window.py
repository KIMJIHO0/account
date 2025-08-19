import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from app.config import (
    CATEGORIES, DATE_FMT, CSV_PATH,
    COLOR_BG, COLOR_ACCENT,
)
from models.transaction import Transaction
from services import storage, analytics

from ui.components.toolbar import Toolbar
from ui.components.transactions_table import TransactionsTable
from ui.components.summary_bar import SummaryBar


def _comma(n: int) -> str:
    return f"{int(n):,}"


class MainWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)

        # --- UI 구성요소
        self.toolbar = Toolbar(self, categories=CATEGORIES, date_fmt=DATE_FMT)
        self.toolbar.pack(fill="x")

        self.table = TransactionsTable(self)
        self.table.pack(fill="both", expand=True, pady=(10, 0))

        self.summary = SummaryBar(self)
        self.summary.pack(fill="x", pady=6)

        # --- 이벤트 연결
        self.toolbar.on_add(self._on_add)
        self.toolbar.on_delete(self._on_delete)
        self.toolbar.on_save(self._on_save)
        self.toolbar.on_chart(self._on_chart)

        # --- 초기 로드
        self._load_data()

    # ---------- 동작 ----------
    def _load_data(self):
        try:
            df = storage.read_all(CSV_PATH)
        except Exception as e:
            messagebox.showerror("오류", f"CSV 읽기 실패: {e}")
            return

        # 테이블 채우기 + 합계 계산
        inc = exp = 0
        rows = []
        for idx, row in df.iterrows():
            amt = int(row["amount"])
            row_type = row["type"]

            tag = "inc" if row_type == "수입" else "exp"
            if row_type == "수입":
                inc += amt
            else:
                exp += amt

            rows.append({
                "values": (
                    row["date"], row_type, row["category"],
                    row["description"], _comma(amt)
                ),
                "odd": (idx % 2 == 1),
                "tag": tag
            })

        self.table.load_rows(rows)

        total = inc - exp
        self.summary.set_text(f"합계: {_comma(total)}원 (수입 {_comma(inc)}원 / 지출 {_comma(exp)}원)")

    def _on_add(self):
        try:
            form = self.toolbar.get_form()
            amt = int(str(form["amount"]).replace(",", "").strip())
            tx = Transaction(
                date=form["date"].strip(),
                type=form["type"].strip(),
                category=form["category"].strip(),
                description=form["description"].strip(),
                amount=amt,
            )
            Transaction.validate(tx)
        except Exception as e:
            messagebox.showwarning("입력 오류", f"잘못된 값: {e}")
            return

        storage.append_row(tx.__dict__)
        self._load_data()
        self.toolbar.clear_desc_and_amount()

    def _on_delete(self):
        sel = self.table.selected_items()
        if not sel:
            messagebox.showinfo("안내", "삭제할 항목을 선택하세요.")
            return

        # 현재 테이블의 모든 행 중 선택된 것 제외하여 CSV로 덮어쓰기
        keep_values = []
        for item_id, values in self.table.iter_all():
            if item_id in sel:
                continue
            vals = list(values)
            vals[4] = int(str(vals[4]).replace(",", ""))  # 금액 콤마 제거
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
        month = self.toolbar.get_month().strip()
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
