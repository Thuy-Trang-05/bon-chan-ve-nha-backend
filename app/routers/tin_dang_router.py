"""
tin_dang_router.py — UC-06, UC-07, UC-10, UC-12, UC-13, UC-15
-----------------------------------------------------------------
    GET  /api/tin-dang                 danh sách + lọc (UC-12), khớp
                                        các tham số Trang Tìm kiếm đã
                                        dùng: loai_thu_cung, loai_tin,
                                        khu_vuc, trang_thai, tu_khoa
    POST /api/tin-dang                 đăng tin mới (UC-06/07), nhận
                                        multipart/form-data (có ảnh)
    GET  /api/tin-dang/{id}            chi tiết 1 tin (UC-10)
    PATCH /api/tin-dang/{id}/trang-thai đánh dấu đã giải quyết (UC-13)
                                        hoặc Admin ẩn tin (UC-16)
    POST /api/tin-dang/{id}/bao-cao    báo cáo vi phạm (UC-15)

Ảnh được lưu vào thư mục /static/uploads (xem main.py mount thư mục
này), đường dẫn lưu vào cột hinh_anh.duong_dan. Trong dự án thật ở quy
mô lớn hơn, nên đổi sang lưu ảnh trên dịch vụ lưu trữ đám mây (S3,
Cloudinary...) thay vì ổ đĩa server — đã ghi ở mục 6.3 Hướng phát triển.
"""

import os
import shutil
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from .. import models, schemas
from ..deps import lay_nguoi_dung_hien_tai

router = APIRouter(prefix="/api/tin-dang", tags=["Tin đăng"])

THU_MUC_UPLOAD = os.path.join("static", "uploads")
os.makedirs(THU_MUC_UPLOAD, exist_ok=True)


def _lay_hoac_tao_loai_thu_cung(db: Session, ten_loai: str) -> models.LoaiThuCung:
    loai = db.query(models.LoaiThuCung).filter(models.LoaiThuCung.ten_loai == ten_loai).first()
    if not loai:
        loai = models.LoaiThuCung(ten_loai=ten_loai)
        db.add(loai)
        db.flush()  # để có loai_id ngay mà chưa cần commit cả transaction
    return loai


@router.get("/cua-toi", response_model=List[schemas.TinDangRa])
def tin_dang_cua_toi(
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.TinDang)
        .options(
            joinedload(models.TinDang.nguoi_dung),
            joinedload(models.TinDang.hinh_anh),
            joinedload(models.TinDang.thu_cung).joinedload(models.ThuCung.loai),
        )
        .filter(models.TinDang.nguoi_dung_id == nguoi_dung_hien_tai.nguoi_dung_id)
        .order_by(models.TinDang.ngay_dang.desc())
        .all()
    )


@router.get("", response_model=List[schemas.TinDangRa])
def danh_sach_tin_dang(
    loai_thu_cung: Optional[str] = None,   # 'Chó' | 'Mèo' | 'Khác'
    loai_tin: Optional[str] = None,        # 'Lạc mất' | 'Tìm thấy'
    khu_vuc: Optional[str] = None,
    trang_thai: Optional[str] = None,      # mặc định chỉ hiện tin đang hiển thị
    tu_khoa: Optional[str] = None,
    trang: int = 1,
    so_luong: int = 20,
    db: Session = Depends(get_db),
):
    truy_van = db.query(models.TinDang).options(
        joinedload(models.TinDang.nguoi_dung),
        joinedload(models.TinDang.hinh_anh),
        joinedload(models.TinDang.thu_cung).joinedload(models.ThuCung.loai),
    )

    if trang_thai:
        truy_van = truy_van.filter(models.TinDang.trang_thai == trang_thai)
    else:
        # Mặc định Khách/Người dùng chỉ thấy tin đang hiển thị — tin đã ẩn
        # (da_an, do Admin gỡ ở UC-16) chỉ hiện khi có tham số trang_thai rõ ràng.
        truy_van = truy_van.filter(models.TinDang.trang_thai != "da_an")

    if loai_tin:
        truy_van = truy_van.filter(models.TinDang.loai_tin == loai_tin)
    if khu_vuc:
        truy_van = truy_van.filter(models.TinDang.khu_vuc == khu_vuc)
    if tu_khoa:
        truy_van = truy_van.filter(models.TinDang.tieu_de.ilike(f"%{tu_khoa}%"))
    if loai_thu_cung:
        truy_van = truy_van.join(models.ThuCung).join(models.LoaiThuCung).filter(
            models.LoaiThuCung.ten_loai == loai_thu_cung
        )

    truy_van = truy_van.order_by(models.TinDang.ngay_dang.desc())
    ket_qua = truy_van.offset((trang - 1) * so_luong).limit(so_luong).all()
    return ket_qua


@router.get("/{tin_dang_id}", response_model=schemas.TinDangRa)
def chi_tiet_tin_dang(tin_dang_id: int, db: Session = Depends(get_db)):
    tin = (
        db.query(models.TinDang)
        .options(
            joinedload(models.TinDang.nguoi_dung),
            joinedload(models.TinDang.hinh_anh),
            joinedload(models.TinDang.thu_cung).joinedload(models.ThuCung.loai),
        )
        .filter(models.TinDang.tin_dang_id == tin_dang_id)
        .first()
    )
    if not tin:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin đăng.")
    return tin


@router.post("", response_model=schemas.TinDangRa, status_code=201)
def dang_tin_moi(
    loai_tin: str = Form(...),
    loai_thu_cung: str = Form(...),
    ten_thu_cung: Optional[str] = Form(None),
    mo_ta: Optional[str] = Form(None),
    khu_vuc: Optional[str] = Form(None),
    vi_do: Optional[float] = Form(None),
    kinh_do: Optional[float] = Form(None),
    hinh_anh: List[UploadFile] = File(default=[]),
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    # 1) Tạo (hoặc lấy) ThuCung để gắn loại — xem ghi chú thiết kế ở đầu models.py
    loai = _lay_hoac_tao_loai_thu_cung(db, loai_thu_cung)
    thu_cung_moi = models.ThuCung(
        ten_thu_cung=ten_thu_cung,
        loai_id=loai.loai_id,
        nguoi_dung_id=nguoi_dung_hien_tai.nguoi_dung_id,
    )
    db.add(thu_cung_moi)
    db.flush()

    # 2) Tạo tin đăng
    tin_moi = models.TinDang(
        nguoi_dung_id=nguoi_dung_hien_tai.nguoi_dung_id,
        thu_cung_id=thu_cung_moi.thu_cung_id,
        loai_tin=loai_tin,
        tieu_de=(ten_thu_cung or "Thú cưng") + " — " + (khu_vuc or "chưa rõ khu vực"),
        mo_ta=mo_ta,
        khu_vuc=khu_vuc,
        vi_do=vi_do,
        kinh_do=kinh_do,
    )
    db.add(tin_moi)
    db.flush()

    # 3) Lưu ảnh (nếu có) vào thư mục static/uploads
    for i, anh in enumerate(hinh_anh):
        phan_mo_rong = os.path.splitext(anh.filename or "")[1] or ".jpg"
        ten_file = f"{uuid.uuid4().hex}{phan_mo_rong}"
        duong_dan_luu = os.path.join(THU_MUC_UPLOAD, ten_file)
        with open(duong_dan_luu, "wb") as f:
            shutil.copyfileobj(anh.file, f)

        db.add(models.HinhAnh(
            tin_dang_id=tin_moi.tin_dang_id,
            duong_dan=f"/static/uploads/{ten_file}",
            la_anh_chinh=(i == 0),
        ))

    db.commit()
    db.refresh(tin_moi)
    return tin_moi


@router.put("/{tin_dang_id}", response_model=schemas.TinDangRa)
def sua_tin_dang(
    tin_dang_id: int,
    du_lieu: schemas.TinDangCapNhat,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    tin = db.get(models.TinDang, tin_dang_id)
    if not tin:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin đăng.")
    if tin.nguoi_dung_id != nguoi_dung_hien_tai.nguoi_dung_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa tin đăng này.")

    if du_lieu.tieu_de is not None:
        tin.tieu_de = du_lieu.tieu_de
    if du_lieu.mo_ta is not None:
        tin.mo_ta = du_lieu.mo_ta
    if du_lieu.khu_vuc is not None:
        tin.khu_vuc = du_lieu.khu_vuc

    db.commit()
    db.refresh(tin)
    return tin


@router.delete("/{tin_dang_id}", status_code=204)
def xoa_tin_dang(
    tin_dang_id: int,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    tin = db.get(models.TinDang, tin_dang_id)
    if not tin:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin đăng.")
    if tin.nguoi_dung_id != nguoi_dung_hien_tai.nguoi_dung_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa tin đăng này.")

    db.delete(tin)
    db.commit()
    return None


@router.patch("/{tin_dang_id}/trang-thai", response_model=schemas.TinDangRa)
def cap_nhat_trang_thai_tin_dang(
    tin_dang_id: int,
    du_lieu: schemas.TinDangCapNhatTrangThai,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    tin = db.get(models.TinDang, tin_dang_id)
    if not tin:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin đăng.")

    # UC-13: chỉ chủ tin hoặc Admin mới được đổi trạng thái
    la_chu_tin = tin.nguoi_dung_id == nguoi_dung_hien_tai.nguoi_dung_id
    la_admin = nguoi_dung_hien_tai.vai_tro == "Admin"
    if not (la_chu_tin or la_admin):
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa tin đăng này.")

    tin.trang_thai = du_lieu.trang_thai
    db.commit()
    db.refresh(tin)
    return tin


@router.post("/{tin_dang_id}/bao-cao", response_model=schemas.BaoCaoRa, status_code=201)
def bao_cao_vi_pham(
    tin_dang_id: int,
    du_lieu: schemas.BaoCaoTao,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    tin = db.get(models.TinDang, tin_dang_id)
    if not tin:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin đăng.")

    bao_cao_moi = models.BaoCaoViPham(
        tin_dang_id=tin_dang_id,
        nguoi_bao_cao_id=nguoi_dung_hien_tai.nguoi_dung_id,
        ly_do=du_lieu.ly_do,
    )
    db.add(bao_cao_moi)
    db.commit()
    db.refresh(bao_cao_moi)
    return bao_cao_moi
