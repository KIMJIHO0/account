import csv
import hashlib
import os
from dataclasses import dataclass
from typing import Optional
from app.config import USERS_CSV, DATA_DIR

SALT = "simple_salt_for_demo_only"  # 데모용. 실제 서비스면 os.urandom + per-user salt 권장.

def _hash(pw: str) -> str:
    return hashlib.sha256((SALT + pw).encode("utf-8")).hexdigest()

@dataclass
class User:
    username: str   # 로그인 아이디
    password_hash: str
    display_name: str  # 화면 표시용(닉네임)

class AuthService:
    def __init__(self, users_csv=USERS_CSV):
        self.users_csv = users_csv
        if not self.users_csv.exists():
            with open(self.users_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["username", "password_hash", "display_name"])

    def register(self, username: str, password: str, display_name: str) -> bool:
        if self.find_user(username):
            return False
        with open(self.users_csv, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([username, _hash(password), display_name])
        # 사용자별 데이터 파일 폴더 준비
        (DATA_DIR).mkdir(parents=True, exist_ok=True)
        return True

    def find_user(self, username: str) -> Optional[User]:
        if not self.users_csv.exists():
            return None
        with open(self.users_csv, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"] == username:
                    return User(row["username"], row["password_hash"], row["display_name"])
        return None

    def login(self, username: str, password: str) -> Optional[User]:
        u = self.find_user(username)
        if not u:
            return None
        if u.password_hash == _hash(password):
            return u
        return None

# 전역 세션(간단)
_current_user: Optional[User] = None

def set_current_user(u: Optional[User]):
    global _current_user
    _current_user = u

def get_current_user() -> Optional[User]:
    return _current_user
