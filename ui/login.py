import tkinter as tk
from tkinter import ttk, messagebox
from services.auth import AuthService, set_current_user
from app.config import COLOR_ACCENT

auth = AuthService()

class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app

        wrapper = ttk.Frame(self)
        wrapper.pack(expand=True)

        title = ttk.Label(wrapper, text="가계부 로그인", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 16))

        ttk.Label(wrapper, text="아이디").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.ent_id = ttk.Entry(wrapper, width=28)
        self.ent_id.grid(row=1, column=1, sticky="w")

        ttk.Label(wrapper, text="비밀번호").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.ent_pw = ttk.Entry(wrapper, show="*", width=28)
        self.ent_pw.grid(row=2, column=1, sticky="w")

        # 버튼들
        btn_login = ttk.Button(wrapper, text="로그인", command=self._login)
        btn_login.grid(row=3, column=0, columnspan=2, pady=(12, 6), ipady=3)

        sep = ttk.Separator(wrapper)
        sep.grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)

        # 회원가입
        ttk.Label(wrapper, text="닉네임").grid(row=5, column=0, sticky="e", padx=6, pady=(6, 2))
        self.ent_nick = ttk.Entry(wrapper, width=28)
        self.ent_nick.grid(row=5, column=1, sticky="w", pady=(6, 2))

        ttk.Label(wrapper, text="새 아이디").grid(row=6, column=0, sticky="e", padx=6, pady=2)
        self.ent_new_id = ttk.Entry(wrapper, width=28)
        self.ent_new_id.grid(row=6, column=1, sticky="w")

        ttk.Label(wrapper, text="새 비밀번호").grid(row=7, column=0, sticky="e", padx=6, pady=2)
        self.ent_new_pw = ttk.Entry(wrapper, show="*", width=28)
        self.ent_new_pw.grid(row=7, column=1, sticky="w")

        ttk.Button(wrapper, text="회원가입", command=self._register).grid(row=8, column=0, columnspan=2, pady=(10, 0), ipady=3)

        # 액센트 색상 살짝
        style = ttk.Style(self)
        style.configure("Accent.TButton", foreground="white", background=COLOR_ACCENT)
        try:
            style.map("Accent.TButton", background=[("active", COLOR_ACCENT)])
            btn_login.configure(style="Accent.TButton")
        except Exception:
            pass

    def _login(self):
        uid = self.ent_id.get().strip()
        pw = self.ent_pw.get().strip()
        u = auth.login(uid, pw)
        if not u:
            messagebox.showerror("로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.")
            return
        set_current_user(u)
        self.app.show("home")

    def _register(self):
        nick = self.ent_nick.get().strip()
        uid = self.ent_new_id.get().strip()
        pw = self.ent_new_pw.get().strip()
        if not (nick and uid and pw):
            messagebox.showwarning("입력", "닉네임/아이디/비밀번호를 모두 입력하세요.")
            return
        ok = auth.register(uid, pw, nick)
        if not ok:
            messagebox.showerror("실패", "이미 사용 중인 아이디입니다.")
            return
        messagebox.showinfo("완료", "회원가입이 완료되었습니다. 위의 로그인 폼으로 로그인하세요.")
