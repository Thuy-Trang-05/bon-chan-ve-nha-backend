
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "doi-chuoi-nay-truoc-khi-trien-khai-that")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_HET_HAN_PHUT = int(os.getenv("JWT_HET_HAN_PHUT", "1440"))

_GIOI_HAN_BYTE_BCRYPT = 72

def bam_mat_khau(mat_khau_goc: str) -> str:
    du_lieu = mat_khau_goc.encode("utf-8")[:_GIOI_HAN_BYTE_BCRYPT]
    return bcrypt.hashpw(du_lieu, bcrypt.gensalt()).decode("utf-8")

def kiem_tra_mat_khau(mat_khau_goc: str, mat_khau_da_bam: str) -> bool:
    du_lieu = mat_khau_goc.encode("utf-8")[:_GIOI_HAN_BYTE_BCRYPT]
    try:
        return bcrypt.checkpw(du_lieu, mat_khau_da_bam.encode("utf-8"))
    except ValueError:

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
