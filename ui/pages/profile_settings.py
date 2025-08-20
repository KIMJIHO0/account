# ui/pages/profile_settings.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from services.auth import AuthService, get_current_user, set_current_user

auth = AuthService()

try:
    # Pillow가 있으면 미리보기 리사이징
    from PIL import Image, ImageTk  # type: ignore
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False


class ProfileDialog(tk.Toplevel):
    """ID는 수정 불가, 닉네임/비번/아바타 변경."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("프로필 설정")
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.resizable(False, False)

        self._user = get_current_user()
        if not self._user:
            messagebox.showwarning("안내", "로그인 후 이용해주세요.")
            self.destroy()
            return

        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        # ID (읽기 전용)
        row0 = ttk.Frame(root); row0.pack(fill="x", pady=(0,8))
        ttk.Label(row0, text="ID", width=14).pack(side="left")
        self.ent_id = ttk.Entry(row0, width=30, state="readonly")
        self.ent_id.pack(side="left", expand=True, fill="x")
        self.ent_id.configure(state="normal"); self.ent_id.insert(0, self._user.username); self.ent_id.configure(state="readonly")

        # 닉네임
        row1 = ttk.Frame(root); row1.pack(fill="x", pady=8)
        ttk.Label(row1, text="닉네임", width=14).pack(side="left")
        self.ent_nick = ttk.Entry(row1)
        self.ent_nick.pack(side="left", expand=True, fill="x")
        self.ent_nick.insert(0, self._user.display_name)

        # 새 비밀번호 / 확인
        row2 = ttk.Frame(root); row2.pack(fill="x", pady=8)
        ttk.Label(row2, text="새 비밀번호", width=14).pack(side="left")
        self.ent_pw = ttk.Entry(row2, show="•")
        self.ent_pw.pack(side="left", expand=True, fill="x")
        self.var_show1 = tk.IntVar(value=0)
        tk.Checkbutton(row2, text="표시", variable=self.var_show1,
                       command=lambda: self.ent_pw.configure(show="" if self.var_show1.get() else "•")).pack(side="left", padx=8)

        row3 = ttk.Frame(root); row3.pack(fill="x", pady=8)
        ttk.Label(row3, text="비밀번호 확인", width=14).pack(side="left")
        self.ent_pw2 = ttk.Entry(row3, show="•")
        self.ent_pw2.pack(side="left", expand=True, fill="x")
        self.var_show2 = tk.IntVar(value=0)
        tk.Checkbutton(row3, text="표시", variable=self.var_show2,
                       command=lambda: self.ent_pw2.configure(show="" if self.var_show2.get() else "•")).pack(side="left", padx=8)

        # 아바타(선택) + 미리보기
        row4 = ttk.Frame(root); row4.pack(fill="x", pady=8)
        ttk.Label(row4, text="프로필 사진", width=14).pack(side="left")
        self.lbl_avatar_path = ttk.Label(row4, text=self._user.avatar or "선택된 파일 없음", width=34)
        self.lbl_avatar_path.pack(side="left", padx=(0,8))
        ttk.Button(row4, text="사진 선택", command=self._choose_avatar).pack(side="left")

        self.preview = ttk.Label(root)
        self.preview.pack(pady=(4, 0))
        self._preview_img = None
        if self._user.avatar:
            self._load_preview(self._user.avatar)

        # 버튼
        btns = ttk.Frame(root); btns.pack(fill="x", pady=(12,0))
        ttk.Button(btns, text="저장", command=self._save).pack(side="right")
        ttk.Button(btns, text="닫기", command=self.destroy).pack(side="right", padx=(0,6))

        # Enter/ESC
        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _choose_avatar(self):
        path = filedialog.askopenfilename(
            title="프로필 사진 선택",
            filetypes=[("이미지 파일", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("모든 파일", "*.*")]
        )
        if not path:
            return
        self.lbl_avatar_path.config(text=path)
        self._load_preview(path)

    def _load_preview(self, path: str):
        if HAVE_PIL:
            try:
                img = Image.open(path)
                img.thumbnail((120, 120))
                self._preview_img = ImageTk.PhotoImage(img)
                self.preview.configure(image=self._preview_img)
            except Exception:
                self.preview.configure(image="", text="(미리보기 실패)")
        else:
            # Pillow 없으면 경로만 표시
            self.preview.configure(text="미리보기는 Pillow 설치 시 가능")

    def _save(self):
        nick = self.ent_nick.get().strip()
        pw1 = self.ent_pw.get().strip()
        pw2 = self.ent_pw2.get().strip()
        if pw1 or pw2:
            if pw1 != pw2:
                messagebox.showwarning("확인", "비밀번호가 일치하지 않습니다.")
                return
            if len(pw1) < 4:
                messagebox.showwarning("확인", "비밀번호는 4자 이상으로 설정하세요.")
                return

        avatar_path = self.lbl_avatar_path.cget("text")
        if avatar_path == "선택된 파일 없음":
            avatar_path = None

        updated = auth.update_profile(
            self._user.username,
            display_name=nick if nick else None,
            new_password=pw1 if pw1 else None,
            avatar_src_path=avatar_path
        )
        if not updated:
            messagebox.showerror("오류", "프로필을 저장할 수 없습니다.")
            return

        # 세션은 update_profile 내에서 갱신됨
        messagebox.showinfo("완료", "프로필이 저장되었습니다.")
        self.destroy()
