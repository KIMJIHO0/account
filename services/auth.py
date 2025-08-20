# services/auth.py
from __future__ import annotations

import json
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

# -------------------------------
# 경로 상수
# -------------------------------
ROOT: Path = Path(__file__).resolve().parents[1]  # 프로젝트 루트(app, data, ui)
DATA_DIR: Path = ROOT / "data"
USERS_JSON: Path = DATA_DIR / "users.json"
AVATAR_DIR: Path = DATA_DIR / "avatars"

DATA_DIR.mkdir(parents=True, exist_ok=True)
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------
# 세션 (현재 로그인 사용자)
# -------------------------------
_CURRENT_USER: Optional["User"] = None


def get_current_user() -> Optional["User"]:
    """현재 로그인된 사용자 객체를 반환합니다. (없으면 None)"""
    return _CURRENT_USER


def set_current_user(user: Optional["User"]) -> None:
    """현재 로그인된 사용자 객체를 설정합니다. (로그아웃 시 None)"""
    global _CURRENT_USER
    _CURRENT_USER = user


# -------------------------------
# 데이터 모델
# -------------------------------
@dataclass
class User:
    username: str
    display_name: str
    password_hash: str
    avatar: Optional[str] = None  # 파일 경로(없을 수 있음)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "User":
        return User(
            username=d["username"],
            display_name=d.get("display_name") or d.get("nickname") or d["username"],
            password_hash=d["password_hash"],
            avatar=d.get("avatar"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "password_hash": self.password_hash,
            "avatar": self.avatar,
        }


# -------------------------------
# 서비스
# -------------------------------
class AuthService:
    """
    파일( users.json )을 사용하여 사용자 등록/로그인/조회/프로필 수정 기능을 제공합니다.
    외부 공개 메서드(API) 시그니처는 기존과 동일합니다.
    """

    # ---------- 초기화 ----------
    def __init__(self) -> None:
        self._ensure_users_file()

    # ---------- Public API ----------
    def register(self, username: str, password: str, display_name: str) -> bool:
        """
        사용자 등록.
        - 중복 ID, 빈 값이면 False
        - 성공 시 True
        """
        username = username.strip()
        if not username or not password or not display_name:
            return False

        db = self._load()
        if username in db:
            return False

        db[username] = User(
            username=username,
            display_name=display_name.strip(),
            password_hash=self._hash(password),
            avatar=None,
        ).to_dict()

        self._save(db)
        return True

    def login(self, username: str, password: str) -> Optional[User]:
        """
        로그인 검증.
        - 성공: User 객체
        - 실패: None
        """
        user_rec = self._load().get(username)
        if not user_rec:
            return None

        if self._hash(password) != user_rec.get("password_hash"):
            return None

        return User.from_dict(user_rec)

    def get_user(self, username: str) -> Optional[User]:
        """username으로 사용자 레코드를 조회."""
        rec = self._load().get(username)
        return User.from_dict(rec) if rec else None

    def update_profile(
        self,
        username: str,
        *,
        display_name: Optional[str] = None,
        new_password: Optional[str] = None,
        avatar_src_path: Optional[str] = None,
    ) -> Optional[User]:
        """
        프로필 수정(닉네임/비밀번호/아바타).
        - username(키)은 변경 불가
        - display_name: 공백이 아니면 갱신
        - new_password: 4자 이상이면 비번 갱신
        - avatar_src_path: 이미지 경로를 data/avatars/<username>.<ext> 로 복사
        """
        db = self._load()
        if username not in db:
            return None

        rec = db[username]

        if display_name and display_name.strip():
            rec["display_name"] = display_name.strip()

        if new_password and new_password.strip():
            if len(new_password) >= 4:
                rec["password_hash"] = self._hash(new_password)
            # 4자 미만은 UI에서 이미 걸러지지만, 여기선 조용히 무시

        if avatar_src_path:
            saved = self._copy_avatar(username, Path(avatar_src_path))
            if saved is not None:
                rec["avatar"] = saved  # 문자열 경로

        db[username] = rec
        self._save(db)

        updated = User.from_dict(rec)

        # 세션 사용자라면 세션도 반영
        cur = get_current_user()
        if cur and cur.username == username:
            set_current_user(updated)

        return updated

    # ---------- 내부 헬퍼 ----------
    def _ensure_users_file(self) -> None:
        """users.json 파일이 없으면 빈 객체로 생성."""
        if not USERS_JSON.exists():
            self._write_json(USERS_JSON, {})

    def _load(self) -> Dict[str, Dict[str, Any]]:
        """users.json을 읽어 dict 반환. 실패 시 빈 dict."""
        self._ensure_users_file()
        try:
            return json.loads(USERS_JSON.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, db: Dict[str, Dict[str, Any]]) -> None:
        """dict를 users.json에 저장(UTF-8, pretty)."""
        self._write_json(USERS_JSON, db)

    @staticmethod
    def _hash(pw: str) -> str:
        """SHA-256 해시(16진수 문자열)"""
        return hashlib.sha256(pw.encode("utf-8")).hexdigest()

    @staticmethod
    def _write_json(path: Path, obj: Any) -> None:
        """JSON 안전 저장(UTF-8, 한글 그대로, 들여쓰기)."""
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _copy_avatar(username: str, src: Path) -> Optional[str]:
        """
        아바타 파일을 data/avatars/<username>.<ext> 로 복사.
        - src가 없거나 복사 실패 시 None
        - 성공 시 저장된 경로 문자열 반환
        """
        if not src.exists():
            return None

        ext = src.suffix.lower() or ".png"
        dst = AVATAR_DIR / f"{username}{ext}"
        try:
            shutil.copyfile(src, dst)
            return str(dst)
        except Exception:
            return None
