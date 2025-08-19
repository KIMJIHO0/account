import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from services import storage, analytics
from services.auth import get_current_user
from app.config import COLOR_BORDER, COLOR_PANEL
from ui.components.topbar import TopBar

class AnalyticsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.topbar = TopBar(self, app, title="분석", show_back=True, back_to="home")
        self.topbar.pack(fill="x")

        content = ttk.Frame(self, style="Page.TFrame")
        content.pack(fill="both", expand=True)

        panel = tk.Frame(content, bg=COLOR_PANEL, highlightthickness=1,
                         highlightbackground=COLOR_BORDER, padx=10, pady=8)
        panel.pack(fill="x")

        ttk.Label(panel, text="월(YYYY-MM)").grid(row=0, column=0, sticky="e")
        self.ent_month = ttk.Entry(panel, width=10)
        self.ent_month.grid(row=0, column=1, padx=(6, 12))
        self.ent_month.insert(0, datetime.now().strftime("%Y-%m"))

        ttk.Button(panel, text="카테고리 막대", command=self._bar).grid(row=0, column=2, padx=4)
        ttk.Button(panel, text="일자 순증감", command=self._line).grid(row=0, column=3, padx=4)
        ttk.Button(panel, text="수입/지출 파이", command=self._pie).grid(row=0, column=4, padx=4)

        self.info = ttk.Label(content, text="월을 입력하고 원하는 그래프 버튼을 클릭하세요.", anchor="w")
        self.info.pack(fill="x", pady=(10,0))

    def on_show(self):
        self.topbar.refresh_user()

    @property
    def _csv_path(self):
        from services.storage import csv_path_for_user
        u = get_current_user()
        return csv_path_for_user(u.username)

    def _get_summary(self):
        month = self.ent_month.get().strip()
        df = storage.read_all(self._csv_path)
        summary = analytics.month_summary(df, month)
        return month, df, summary

    def _bar(self):
        month, df, summary = self._get_summary()
        if summary.empty:
            messagebox.showinfo("안내", f"{month} 데이터가 없습니다."); return
        plt.figure(); plt.title(f"{month} 카테고리별 수입/지출")
        x = range(len(summary))
        plt.bar(x, summary["수입"], label="수입", linewidth=0)
        plt.bar(x, -summary["지출"], label="지출", linewidth=0)
        plt.xticks(x, summary["category"], rotation=30)
        plt.legend(); plt.tight_layout(); plt.show()

    def _line(self):
        month, df, _ = self._get_summary()
        ser = analytics.daily_net_series(df, month)
        if ser.size == 0:
            messagebox.showinfo("안내", f"{month} 데이터가 없습니다."); return
        plt.figure(); plt.title(f"{month} 일자별 순증감(수입-지출)")
        plt.plot(list(ser.index), list(ser.values), marker="o")
        plt.xticks(rotation=45)
        plt.tight_layout(); plt.show()

    def _pie(self):
        month, df, summary = self._get_summary()
        if summary.empty:
            messagebox.showinfo("안내", f"{month} 데이터가 없습니다."); return
        total_inc = float(summary["수입"].sum()); total_exp = float(summary["지출"].sum())
        plt.figure(); plt.title(f"{month} 수입/지출 비중")
        plt.pie([total_inc, total_exp], labels=["수입", "지출"], autopct="%.1f%%", startangle=90)
        plt.axis("equal"); plt.show()
