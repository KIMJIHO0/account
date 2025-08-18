import tkinter as tk
from tkinter import ttk
from ui.main_window import MainWindow

def run_app():
    root = tk.Tk()
    root.title("가계부 - Python (tkinter)")
    root.geometry("900x600")
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    MainWindow(root)
    root.mainloop()
