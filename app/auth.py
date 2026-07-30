"""
auth.py — Mã hóa mật khẩu (bcrypt) và xác thực JWT (mục 2.3.5)
-----------------------------------------------------------------
Đúng như tiểu luận đã trình bày:
  "Mật khẩu được mã hóa bằng bcrypt trước khi lưu vào database, nên kể
   cả khi database bị lộ, kẻ tấn công cũng không đọc được mật khẩu gốc."
  "Client gửi email/mật khẩu để đăng nhập → Server kiểm tra, nếu đúng
   thì trả về JWT → Client đính token vào header Authorization của các
   request tiếp theo."

Dùng thẳng thư viện bcrypt (không qua lớp trung gian passlib) — passlib
đã cũ (2020) và từng gây lỗi "password cannot be longer than 72 bytes"
không ổn định giữa các phiên bản Python/bcrypt khác nhau (gặp cả trên
máy cá nhân lẫn trên Railway khi dùng Python 3.13). Gọi thẳng bcrypt
tránh hẳn lớp tương thích đó.

bam_mat_khau() / kiem_tra_mat_khau(): mã hóa/so khớp mật khẩu bằng bcrypt.
tao_jwt(): ký JWT gồm claim "sub" (nguoi_dung_id) và "vai_tro" — claim
  vai_tro chính là thứ TrangAdmin.jsx (frontend) cần đọc để quyết định
  có cho vào /admin hay không (đã ghi chú ở đầu file TrangAdmin.jsx).
giai_ma_jwt(): kiểm tra chữ ký + hạn dùng của token, dùng trong deps.py.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "doi-chuoi-nay-truoc-khi-trien-khai-that")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_HET_HAN_PHUT = int(os.getenv("JWT_HET_HAN_PHUT", "1440"))  # mặc định 24 giờ

# bcrypt chỉ nhận tối đa 72 byte — cắt bớt cho an toàn thay vì để lỗi
# nếu ai đó lỡ nhập mật khẩu quá dài.
_GIOI_HAN_BYTE_BCRYPT = 72


def bam_mat_khau(mat_khau_goc: str) -> str:
    du_lieu = mat_khau_goc.encode("utf-8")[:_GIOI_HAN_BYTE_BCRYPT]
    return bcrypt.hashpw(du_lieu, bcrypt.gensalt()).decode("utf-8")


def kiem_tra_mat_khau(mat_khau_goc: str, mat_khau_da_bam: str) -> bool:
    du_lieu = mat_khau_goc.encode("utf-8")[:_GIOI_HAN_BYTE_BCRYPT]
    try:
        return bcrypt.checkpw(du_lieu, mat_khau_da_bam.encode("utf-8"))
    except ValueError:
        # mat_khau_da_bam không đúng định dạng bcrypt (vd: dữ liệu cũ hỏng)
        return False


def tao_jwt(nguoi_dung_id: int, vai_tro: str) -> str:
    het_han = datetime.now(timezone.utc) + timedelta(minutes=JWT_HET_HAN_PHUT)
    du_lieu = {"sub": str(nguoi_dung_id), "vai_tro": vai_tro, "exp": het_han}
    return jwt.encode(du_lieu, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def giai_ma_jwt(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
