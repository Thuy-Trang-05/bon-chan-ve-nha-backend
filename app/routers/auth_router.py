"""
auth_router.py — UC-01 (Đăng ký) và UC-02 (Đăng nhập)
-----------------------------------------------------------------
Khớp đúng với ghi chú "Ghi chú tích hợp API thật" ở đầu file
DangNhapDangKy.jsx (frontend):
    POST /api/auth/dang-ky   body: { email, mat_khau, ho_ten, so_dien_thoai }
    POST /api/auth/dang-nhap body: { email, mat_khau }
                             trả về { access_token, token_type, nguoi_dung }
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import bam_mat_khau, kiem_tra_mat_khau, tao_jwt

router = APIRouter(prefix="/api/auth", tags=["Xác thực"])


@router.post("/dang-ky", response_model=schemas.TokenRa, status_code=status.HTTP_201_CREATED)
def dang_ky(du_lieu: schemas.DangKyTao, db: Session = Depends(get_db)):
    da_ton_tai = db.query(models.NguoiDung).filter(models.NguoiDung.email == du_lieu.email).first()
    if da_ton_tai:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký.")

    nguoi_dung_moi = models.NguoiDung(
        email=du_lieu.email,
        mat_khau=bam_mat_khau(du_lieu.mat_khau),
        ho_ten=du_lieu.ho_ten,
        so_dien_thoai=du_lieu.so_dien_thoai,
        vai_tro="User",
    )
    db.add(nguoi_dung_moi)
    db.commit()
    db.refresh(nguoi_dung_moi)

    token = tao_jwt(nguoi_dung_moi.nguoi_dung_id, nguoi_dung_moi.vai_tro)
    return schemas.TokenRa(access_token=token, nguoi_dung=nguoi_dung_moi)


@router.post("/dang-nhap", response_model=schemas.TokenRa)
def dang_nhap(du_lieu: schemas.DangNhapTao, db: Session = Depends(get_db)):
    nguoi_dung = db.query(models.NguoiDung).filter(models.NguoiDung.email == du_lieu.email).first()

    loi_sai_thong_tin = HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng.")
    if not nguoi_dung:
        raise loi_sai_thong_tin
    if not kiem_tra_mat_khau(du_lieu.mat_khau, nguoi_dung.mat_khau):
        raise loi_sai_thong_tin
    if not nguoi_dung.dang_hoat_dong:
        raise HTTPException(status_code=403, detail="Tài khoản này đã bị quản trị viên khóa.")

    token = tao_jwt(nguoi_dung.nguoi_dung_id, nguoi_dung.vai_tro)
    return schemas.TokenRa(access_token=token, nguoi_dung=nguoi_dung)
