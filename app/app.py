import tkinter as tk
from tkinter import ttk

try:
    import sv_ttk
    HAVE_SV = True
except:
    HAVE_SV = False

from ui.login import LoginFrame
from ui.home import HomeFrame
from ui.pages.account_book import AccountBookPage
from ui.pages.analytics_page import AnalyticsPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("가계부 - Python (tkinter)")
        self.geometry("1280x720")
        self.minsize(1120, 620)

        # 기본 폰트/여백(윈도우에서 한글 가독)
        self.option_add("*Font", "{Malgun Gothic} 10")
        self.option_add("*TButton.Padding", 6)
        self.option_add("*TEntry.Padding", 4)
        self.option_add("*TCombobox.Padding", 4)

        if HAVE_SV:
            sv_ttk.set_theme("light")

        # 공통 스타일(라이트 톤)
        style = ttk.Style(self)
        style.configure("Page.TFrame", padding=12)
        style.configure("Card.TFrame", relief="flat")
        style.configure("Accent.TButton", padding=(10,6))
        # 버튼 hover 느낌 (sv-ttk 사용시 더 자연스러움)
        try:
            style.map("Accent.TButton", background=[("active", "#4f46e5")])
        except Exception:
            pass

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        def add(frame_cls, name):
            frame = frame_cls(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        add(LoginFrame, "login")
        add(HomeFrame, "home")
        add(AccountBookPage, "account")
        add(AnalyticsPage, "analytics")

        self.show("login")

    def show(self, name: str):
        f = self.frames[name]
        if hasattr(f, "on_show"):
            f.on_show()
        f.tkraise()

if __name__ == "__main__":
    App().mainloop()
