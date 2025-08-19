import tkinter as tk
from tkinter import ttk, messagebox

from services.auth import AuthService, set_current_user

auth = AuthService()


class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # ===== 배경(그라데이션) 캔버스 =====
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._redraw)

        # 카드 기본 값 (버튼이 안 잘리도록 높이 넉넉하게)
        self.card_w, self.card_h = 560, 520
        self.card_radius = 22
        self.card_fill = "#ffffff"
        self.card_outline = "#d6c3d4"

        # 카드 안쪽 실제 폼 영역(프레임)
        self.form = tk.Frame(self.canvas, bg=self.card_fill)
        self.form_id = self.canvas.create_window(0, 0, window=self.form, anchor="center")

        # 두 화면을 스택으로 구성
        self.login_view = tk.Frame(self.form, bg=self.card_fill)
        self.signup_view = tk.Frame(self.form, bg=self.card_fill)
        for v in (self.login_view, self.signup_view):
            v.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.86)

        # 화면 구성
        self._build_login(self.login_view)
        self._build_signup(self.signup_view)

        # 시작은 로그인 화면
        self._show("login")

    # ------------------ 배경/카드 그리기 ------------------
    def _draw_gradient(self, w, h, c1="#cc8e96", c2="#8b7bb1"):
        """세로 그라데이션"""
        self.canvas.delete("grad")
        steps = max(h, 1)
        r1, g1, b1 = self.winfo_rgb(c1)
        r2, g2, b2 = self.winfo_rgb(c2)
        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            color = f"#{r//256:02x}{g//256:02x}{b//256:02x}"
            self.canvas.create_line(0, i, w, i, fill=color, tags="grad")

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        """라운드 카드(폴리곤)"""
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, splinesteps=36, **kw)

    def _redraw(self, _event=None):
        # 배경
        w = max(self.winfo_width(), 1)
        h = max(self.winfo_height(), 1)
        self._draw_gradient(w, h)

        # 화면 크기에 맞춰 카드 크기 살짝 적응
        cw = min(self.card_w, max(380, w - 60))
        ch = min(self.card_h, max(380, h - 60))

        # 카드 위치
        cx, cy = w // 2, h // 2
        x1 = cx - cw // 2
        y1 = cy - ch // 2
        x2 = cx + cw // 2
        y2 = cy + ch // 2

        # 카드 다시 그림
        self.canvas.delete("card")
        self._round_rect(x1, y1, x2, y2, self.card_radius,
                         fill=self.card_fill, outline=self.card_outline, width=2, tags="card")

        # 폼 프레임 위치/크기
        self.canvas.coords(self.form_id, cx, cy)
        self.canvas.itemconfig(self.form_id, width=cw - 32, height=ch - 32)

    # ------------------ 공용: 한 줄 입력(row) ------------------
    def _row_entry(self, parent, placeholder, *, is_password=False):
        """같은 폭/여백으로 맞춘 한 줄 입력. 비번이면 '표시' 체크박스 포함."""
        row = tk.Frame(parent, bg=self.card_fill)
        row.pack(pady=8, fill="x")
        ent = ttk.Entry(row)
        self._placeholder(ent, placeholder, is_password=is_password)
        ent.pack(side="left", expand=True, fill="x", ipady=8)
        var = None
        if is_password:
            var = tk.IntVar(value=0)
            tk.Checkbutton(
                row, text="표시", variable=var, bg=self.card_fill,
                command=lambda e=ent, v=var: self._toggle_pw(e, v.get())
            ).pack(side="left", padx=(10, 0))
        return ent, var

    # ------------------ 로그인 화면 ------------------
    def _build_login(self, root):
        tk.Label(root, text="Login", bg=self.card_fill,
                 font=("Malgun Gothic", 28, "bold")).pack(pady=(6, 18))

        self.l_id, _ = self._row_entry(root, "ID")
        self.l_pw, self.l_pw_show = self._row_entry(root, "Password", is_password=True)

        tk.Button(root, text="Login", command=self._login,
                  bg="#f6b981", activebackground="#f0a960",
                  fg="black", relief="flat", height=2, width=24,
                  cursor="hand2").pack(pady=(16, 6))

        # 링크: 회원가입
        wrap = tk.Frame(root, bg=self.card_fill)
        wrap.pack(pady=(8, 0))
        tk.Label(wrap, text="계정이 없으신가요? ",
                 bg=self.card_fill, fg="#6b7280").pack(side="left")
        link = tk.Label(wrap, text="회원가입", bg=self.card_fill,
                        fg="#f0a960", cursor="hand2", font=("Malgun Gothic", 10, "bold", "underline"))
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._show("signup"))

        # Enter로 제출
        root.bind_all("<Return>", self._enter_login)

    def _enter_login(self, _e=None):
        if str(self.login_view) in str(self.focus_get()):
            self._login()

    # ------------------ 회원가입 화면 ------------------
    def _build_signup(self, root):
        tk.Label(root, text="Sign Up", bg=self.card_fill,
                 font=("Malgun Gothic", 28, "bold")).pack(pady=(6, 18))

        self.s_id, _ = self._row_entry(root, "ID (Username)")
        self.s_nick, _ = self._row_entry(root, "Nickname")
        self.s_pw, self.s_pw_show = self._row_entry(root, "Password", is_password=True)
        self.s_pw2, self.s_pw2_show = self._row_entry(root, "Confirm Password", is_password=True)

        tk.Button(root, text="Sign Up", command=self._signup,
                  bg="#f6b981", activebackground="#f0a960",
                  fg="black", relief="flat", height=2, width=24,
                  cursor="hand2").pack(pady=(16, 6))

        wrap = tk.Frame(root, bg=self.card_fill)
        wrap.pack(pady=(8, 0))
        tk.Label(wrap, text="이미 계정이 있으신가요? ",
                 bg=self.card_fill, fg="#6b7280").pack(side="left")
        link = tk.Label(wrap, text="로그인", bg=self.card_fill,
                        fg="#f0a960", cursor="hand2", font=("Malgun Gothic", 10, "bold", "underline"))
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._show("login"))

        root.bind_all("<Return>", self._enter_signup)

    def _enter_signup(self, _e=None):
        if str(self.signup_view) in str(self.focus_get()):
            self._signup()

    # ------------------ 화면 전환 ------------------
    def _show(self, which: str):
        if which == "login":
            self.signup_view.lower(self.login_view)
            self.login_view.lift()
            self.l_id.focus_set()
        else:
            self.login_view.lower(self.signup_view)
            self.signup_view.lift()
            self.s_id.focus_set()

    # ------------------ 동작 ------------------
    def _login(self):
        uid = self._read(self.l_id)
        pw = self._read(self.l_pw)
        if not uid or not pw:
            messagebox.showwarning("입력", "ID와 비밀번호를 입력해주세요.")
            return
        u = auth.login(uid, pw)
        if not u:
            messagebox.showerror("로그인 실패", "ID 또는 비밀번호가 올바르지 않습니다.")
            return
        set_current_user(u)
        self.app.show("home")

    def _signup(self):
        uid = self._read(self.s_id)
        nick = self._read(self.s_nick)
        pw = self._read(self.s_pw)
        pw2 = self._read(self.s_pw2)

        if not (uid and nick and pw and pw2):
            messagebox.showwarning("입력", "모든 항목을 입력해주세요.")
            return
        if pw != pw2:
            messagebox.showwarning("입력", "비밀번호가 일치하지 않습니다.")
            return
        ok = auth.register(uid, pw, nick)
        if not ok:
            messagebox.showerror("실패", "이미 사용 중인 ID입니다.")
            return
        messagebox.showinfo("완료", "회원가입이 완료되었습니다. 로그인 해주세요.")
        self._show("login")

    # ------------------ 유틸 ------------------
    def _placeholder(self, entry: ttk.Entry, text: str, *, is_password=False):
        """엔트리에 플레이스홀더 적용"""
        entry._ph_text = text
        entry._ph_is_pw = is_password
        entry._ph_active = True

        def put():
            entry.delete(0, "end")
            entry.insert(0, text)
            entry.configure(foreground="#9ca3af")
            if is_password:
                entry.configure(show="")

        def focus_in(_):
            if entry._ph_active:
                entry.delete(0, "end")
                entry.configure(foreground="black")
                if is_password:
                    entry.configure(show="•")

        def focus_out(_):
            if not entry.get():
                entry._ph_active = True
                put()
            else:
                entry._ph_active = False

        put()
        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)

    def _read(self, entry: ttk.Entry) -> str:
        """플레이스홀더가 표시 중이면 빈 값으로 간주"""
        val = entry.get().strip()
        return "" if getattr(entry, "_ph_active", False) else val

    def _toggle_pw(self, entry: ttk.Entry, show_flag: int):
        """비밀번호 표시/숨김 토글 (플레이스홀더일 땐 항상 평문)"""
        if getattr(entry, "_ph_active", False):
            entry.configure(show="")
            return
        entry.configure(show="" if show_flag else "•")
