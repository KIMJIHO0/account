import tkinter as tk
from tkinter import ttk
from ui.main_window import MainWindow
from app.config import FONT_FAMILY, FONT_SIZE, COLOR_BG, COLOR_TEXT, ROW_HEIGHT

def _init_styles(root: tk.Tk):
    style = ttk.Style(root)
    # 테마 선택 (Windows면 'vista', 그 외 'clam')
    try:
        style.theme_use("vista")
    except tk.TclError:
        style.theme_use("clam")

    root.configure(bg=COLOR_BG)

    # 전역 폰트/패딩 조정
    style.configure(".", font=(FONT_FAMILY, FONT_SIZE))
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT)
    style.configure("TFrame", background=COLOR_BG)
    style.configure("TButton", padding=6)
    style.configure("TCombobox", padding=4)

    # 트리뷰 모양 개선
    style.configure(
        "Treeview",
        rowheight=ROW_HEIGHT,
        font=(FONT_FAMILY, FONT_SIZE),
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        font=(FONT_FAMILY, FONT_SIZE, "bold")
    )

def run_app():
    root = tk.Tk()
    root.title("가계부 - Python (tkinter)")
    root.geometry("1000x640")
    _init_styles(root)
    MainWindow(root)
    root.mainloop()
