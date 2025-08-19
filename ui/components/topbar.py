import tkinter as tk
from tkinter import ttk
from services.auth import get_current_user, set_current_user

class TopBar(ttk.Frame):
    def __init__(self, parent, app, *, title="", show_back=False, back_to=None):
        super().__init__(parent)
        self.app = app
        self._back_to = back_to
        self._last_user_text = None  # 중복 갱신 방지

        # 바 전체 패딩 + 고정 높이 느낌
        self.configure(padding=(16, 8))
        self.grid_columnconfigure(1, weight=1)   # [0]=뒤로, [1]=제목(가변), [2]=우측 영역

        # ← 뒤로
        if show_back and back_to:
            self.btn_back = ttk.Button(self, text="← 뒤로", command=lambda: self.app.show(back_to))
            self.btn_back.grid(row=0, column=0, sticky="w", padx=(0, 10))
        else:
            # 자리 확보용 더미(없어도 되지만, 칼럼 폭 일정 유지를 원하면 주석 해제)
            # ttk.Label(self, text="").grid(row=0, column=0, sticky="w")
            pass

        # 제목(가변 칼럼)
        self.lbl_title = ttk.Label(self, text=title, font=("Malgun Gothic", 12, "bold"))
        self.lbl_title.grid(row=0, column=1, sticky="w")

        # 우측 영역(프로필칩 + 로그아웃)
        right = ttk.Frame(self)
        right.grid(row=0, column=2, sticky="e")

        # 프로필 칩: 고정 글자폭으로 폭 변동 방지 (문자 단위)
        # ttk.Label은 테마에 따라 배경색 적용이 흐릴 수 있어 tk.Label 사용
        self.lbl_user = tk.Label(
            right, text="", bd=0, padx=10, pady=4,
            bg="#eef1ff", fg="#374151"
        )
        self.lbl_user.configure(width=24, anchor="e")  # 💡 폭 고정(24글자), 오른쪽 정렬
        self.lbl_user.grid(row=0, column=0, sticky="e")

        self.btn_logout = ttk.Button(right, text="로그아웃", command=self._logout)
        self.btn_logout.grid(row=0, column=1, padx=(8, 0), sticky="e")

        # 하단 구분선(TopBar 내부에!)
        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))

    def set_title(self, text: str):
        self.lbl_title.config(text=text)

    def refresh_user(self):
        u = get_current_user()
        new_text = f"{u.display_name}  ({u.username})" if u else ""
        # 같은 텍스트면 레이아웃 다시 안 건드림
        if new_text != self._last_user_text:
            self.lbl_user.config(text=new_text)
            self._last_user_text = new_text

    def _logout(self):
        set_current_user(None)
        self.app.show("login")
