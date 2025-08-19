

import tkinter as tk
from tkinter import ttk
from ui.main_window import MainWindow
from app.config import FONT_FAMILY, FONT_SIZE, COLOR_BG, COLOR_TEXT, ROW_HEIGHT

def _init_styles(root: tk.Tk):
    """
    전역 ttk 스타일을 설정합니다.
    - 테마 선택(vista/clam)
    - 기본 폰트, 배경색, 버튼/콤보박스 패딩
    - Treeview(표)의 행 높이, 헤더 폰트 등
    """
    style = ttk.Style(root)
    try:
        style.theme_use("vista")  # Windows 면 'vista'가 보기 좋음
    except tk.TclError:
        style.theme_use("clam")   # 다른 OS 대비

    root.configure(bg=COLOR_BG)

    style.configure(".", font=(FONT_FAMILY, FONT_SIZE))
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT)
    style.configure("TFrame", background=COLOR_BG)
    style.configure("TButton", padding=6)
    style.configure("TCombobox", padding=4)
    style.configure("Treeview", rowheight=ROW_HEIGHT, font=(FONT_FAMILY, FONT_SIZE), borderwidth=0)
    style.configure("Treeview.Heading", font=(FONT_FAMILY, FONT_SIZE, "bold"))

def run_app():
    """
    - Tk 루트 윈도우 생성
    - 전역 스타일 적용
    - MainWindow(실제 화면) 부착
    - mainloop()로 이벤트 루프 시작
    """
    root = tk.Tk()
    root.title("가계부 - Python (tkinter)")
    root.geometry("1000x640")
    _init_styles(root)
    MainWindow(root)  # 메인 화면 위젯(프레임)을 붙임
    root.mainloop()
