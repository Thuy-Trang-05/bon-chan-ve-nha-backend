"""
auth.py — Mã hóa mật khẩu (bcrypt) và xác thực JWT (mục 2.3.5)
-----------------------------------------------------------------
Đúng như tiểu luận đã trình bày:
  "Mật khẩu được mã hóa bằng bcrypt trước khi lưu vào database, nên kể
   cả khi database bị lộ, kẻ tấn công cũng không đọc được mật khẩu gốc."
  "Client gửi email/mật khẩu để đăng nhập → Server kiểm tra, nếu đúng
   thì trả về JWT → Client đính token vào header Authorization của các
   request tiếp theo."

bam_mat_khau() / kiem_tra_mat_khau(): dùng passlib (thuật toán bcrypt).
tao_jwt(): ký JWT gồm claim "sub" (nguoi_dung_id) và "vai_tro" — claim
  vai_tro chính là thứ TrangAdmin.jsx (frontend) cần đọc để quyết định
  có cho vào /admin hay không (đã ghi chú ở đầu file TrangAdmin.jsx).
giai_ma_jwt(): kiểm tra chữ ký + hạn dùng của token, dùng trong deps.py.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "doi-chuoi-nay-truoc-khi-trien-khai-that")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_HET_HAN_PHUT = int(os.getenv("JWT_HET_HAN_PHUT", "1440"))  # mặc định 24 giờ

_ngu_canh_mat_khau = CryptContext(schemes=["bcrypt"], deprecated="auto")


def bam_mat_khau(mat_khau_goc: str) -> str:
    return _ngu_canh_mat_khau.hash(mat_khau_goc)


def kiem_tra_mat_khau(mat_khau_goc: str, mat_khau_da_bam: str) -> bool:
    return _ngu_canh_mat_khau.verify(mat_khau_goc, mat_khau_da_bam)


def tao_jwt(nguoi_dung_id: int, vai_tro: str) -> str:
    het_han = datetime.now(timezone.utc) + timedelta(minutes=JWT_HET_HAN_PHUT)
    du_lieu = {"sub": str(nguoi_dung_id), "vai_tro": vai_tro, "exp": het_han}
    return jwt.encode(du_lieu, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def giai_ma_jwt(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
