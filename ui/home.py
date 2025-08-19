import tkinter as tk
from tkinter import ttk
from ui.components.topbar import TopBar

class HomeFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.topbar = TopBar(self, app, title="홈")
        self.topbar.pack(fill="x")

        page = ttk.Frame(self, style="Page.TFrame")
        page.pack(fill="both", expand=True)

        grid = ttk.Frame(page)
        grid.pack(expand=True)

        # 카드 공용 빌더
        def make_card(parent, emoji, title, desc, cmd):
            outer = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#e5e7eb")
            outer.bind("<Button-1>", lambda e: cmd())
            outer.configure(cursor="hand2")

            header = ttk.Label(outer, text=f"{emoji} {title}", font=("Malgun Gothic", 12, "bold"))
            header.pack(anchor="w", padx=16, pady=(14,4))

            sub = ttk.Label(outer, text=desc, foreground="#6b7280")
            sub.pack(anchor="w", padx=16, pady=(0,14))

            # hover 효과
            def on_enter(_): outer.config(highlightbackground="#c7d2fe")
            def on_leave(_): outer.config(highlightbackground="#e5e7eb")
            outer.bind("<Enter>", on_enter); outer.bind("<Leave>", on_leave)
            return outer

        card1 = make_card(
            grid, "📒", "가계부 작성/조회",
            "수입·지출 기록, 삭제, 월별 합계 확인",
            lambda: self.app.show("account")
        )
        card2 = make_card(
            grid, "📈", "분석/그래프",
            "카테고리/일자별 그래프 및 비중 확인",
            lambda: self.app.show("analytics")
        )

        # 카드 배치
        for i, card in enumerate((card1, card2)):
            card.grid(row=0, column=i, padx=12, pady=12, sticky="nsew")
            card.configure(width=420, height=140)
            card.grid_propagate(False)  # 고정 크기

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_rowconfigure(0, weight=1)

    def on_show(self):
        self.topbar.refresh_user()
