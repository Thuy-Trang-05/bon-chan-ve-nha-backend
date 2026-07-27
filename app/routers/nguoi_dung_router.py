"""
nguoi_dung_router.py — Hồ sơ cá nhân (TrangCaNhan.jsx)
-----------------------------------------------------------------
    GET  /api/nguoi-dung/toi       lấy thông tin người đang đăng nhập
    PUT  /api/nguoi-dung/toi       cập nhật họ tên / số điện thoại
    POST /api/nguoi-dung/toi/anh   tải lên / đổi ảnh đại diện
"""

import os
import shutil
import uuid

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..deps import lay_nguoi_dung_hien_tai

router = APIRouter(prefix="/api/nguoi-dung", tags=["Người dùng"])

THU_MUC_UPLOAD = os.path.join("static", "uploads")
os.makedirs(THU_MUC_UPLOAD, exist_ok=True)


@router.get("/toi", response_model=schemas.NguoiDungRa)
def xem_thong_tin_cua_toi(
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
):
    return nguoi_dung_hien_tai


@router.put("/toi", response_model=schemas.NguoiDungRa)
def cap_nhat_thong_tin_cua_toi(
    du_lieu: schemas.NguoiDungCapNhat,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    if du_lieu.ho_ten is not None:
        nguoi_dung_hien_tai.ho_ten = du_lieu.ho_ten
    if du_lieu.so_dien_thoai is not None:
        nguoi_dung_hien_tai.so_dien_thoai = du_lieu.so_dien_thoai

    db.commit()
    db.refresh(nguoi_dung_hien_tai)
    return nguoi_dung_hien_tai


@router.post("/toi/anh", response_model=schemas.NguoiDungRa)
def doi_anh_dai_dien(
    anh: UploadFile = File(...),
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    phan_mo_rong = os.path.splitext(anh.filename or "")[1] or ".jpg"
    ten_file = f"{uuid.uuid4().hex}{phan_mo_rong}"
    duong_dan_luu = os.path.join(THU_MUC_UPLOAD, ten_file)
    with open(duong_dan_luu, "wb") as f:
        shutil.copyfileobj(anh.file, f)

    nguoi_dung_hien_tai.anh_dai_dien = f"/static/uploads/{ten_file}"
    db.commit()
    db.refresh(nguoi_dung_hien_tai)
    return nguoi_dung_hien_tai
