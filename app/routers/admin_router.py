"""
admin_router.py — Trang quản trị (TrangAdmin.jsx), chỉ Admin dùng được
-----------------------------------------------------------------
Mọi route trong file này đều bọc bằng Depends(yeu_cau_admin) — tương
ứng ghi chú đầu file TrangAdmin.jsx: "kiểm tra role trong JWT trước
khi hiển thị (đã trình bày ở mục 2.3.5)".

    GET   /api/admin/thong-ke              số liệu tổng quan
    GET   /api/admin/tin-dang              toàn bộ tin đăng (kể cả đã ẩn)
    PATCH /api/admin/tin-dang/{id}/an      gỡ tin vi phạm (UC-16)
    PATCH /api/admin/tin-dang/{id}/hien    khôi phục tin đã gỡ
    GET   /api/admin/nguoi-dung            danh sách người dùng (UC-17)
    PATCH /api/admin/nguoi-dung/{id}/khoa  khóa / mở khóa tài khoản
    GET   /api/admin/bao-cao               danh sách báo cáo vi phạm
                                            (kèm tên tin, người báo cáo,
                                            người bị báo cáo — dùng cho
                                            UC-17 đối chiếu hồ sơ)
    PATCH /api/admin/bao-cao/{id}/xu-ly    đánh dấu báo cáo đã xử lý
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from ..database import get_db
from .. import models, schemas
from ..deps import yeu_cau_admin

router = APIRouter(prefix="/api/admin", tags=["Quản trị"], dependencies=[Depends(yeu_cau_admin)])


@router.get("/thong-ke")
def thong_ke_tong_quan(db: Session = Depends(get_db)):
    return {
        "tong_tin_dang": db.query(func.count(models.TinDang.tin_dang_id)).scalar(),
        "da_giai_quyet": db.query(func.count(models.TinDang.tin_dang_id))
            .filter(models.TinDang.trang_thai == "da_giai_quyet").scalar(),
        "tong_nguoi_dung": db.query(func.count(models.NguoiDung.nguoi_dung_id)).scalar(),
        "bao_cao_cho_xu_ly": db.query(func.count(models.BaoCaoViPham.bao_cao_id))
            .filter(models.BaoCaoViPham.trang_thai == "cho_xu_ly").scalar(),
    }


@router.get("/tin-dang", response_model=List[schemas.TinDangRa])
def quan_ly_tin_dang(db: Session = Depends(get_db)):
    return (
        db.query(models.TinDang)
        .options(
            joinedload(models.TinDang.nguoi_dung),
            joinedload(models.TinDang.hinh_anh),
            joinedload(models.TinDang.thu_cung).joinedload(models.ThuCung.loai),
        )
        .order_by(models.TinDang.ngay_dang.desc())
        .all()
    )


@router.patch("/tin-dang/{tin_dang_id}/an", response_model=schemas.TinDangRa)
def an_tin_dang(tin_dang_id: int, db: Session = Depends(get_db)):
    tin = db.get(models.TinDang, tin_dang_id)
    if not tin:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin đăng.")
    tin.trang_thai = "da_an"
    db.commit()
    db.refresh(tin)
    return tin


@router.patch("/tin-dang/{tin_dang_id}/hien", response_model=schemas.TinDangRa)
def khoi_phuc_tin_dang(tin_dang_id: int, db: Session = Depends(get_db)):
    tin = db.get(models.TinDang, tin_dang_id)
    if not tin:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin đăng.")
    tin.trang_thai = "dang_hien_thi"
    db.commit()
    db.refresh(tin)
    return tin


@router.get("/nguoi-dung", response_model=List[schemas.NguoiDungRa])
def quan_ly_nguoi_dung(db: Session = Depends(get_db)):
    return db.query(models.NguoiDung).order_by(models.NguoiDung.ngay_tao.desc()).all()


@router.patch("/nguoi-dung/{nguoi_dung_id}/khoa", response_model=schemas.NguoiDungRa)
def khoa_mo_khoa_tai_khoan(nguoi_dung_id: int, db: Session = Depends(get_db)):
    nd = db.get(models.NguoiDung, nguoi_dung_id)
    if not nd:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    if nd.vai_tro == "Admin":
        raise HTTPException(status_code=400, detail="Không thể khóa tài khoản Admin.")
    nd.dang_hoat_dong = not nd.dang_hoat_dong
    db.commit()
    db.refresh(nd)
    return nd


@router.get("/bao-cao", response_model=List[schemas.BaoCaoRa])
def quan_ly_bao_cao(db: Session = Depends(get_db)):
    danh_sach = (
        db.query(models.BaoCaoViPham)
        .options(
            joinedload(models.BaoCaoViPham.nguoi_bao_cao),
            joinedload(models.BaoCaoViPham.tin_dang).joinedload(models.TinDang.nguoi_dung),
        )
        .order_by(models.BaoCaoViPham.gui_luc.desc())
        .all()
    )
    # Không dùng response_model tự động serialize trực tiếp từ ORM được vì
    # tieu_de_tin/nguoi_bi_bao_cao là dữ liệu ghép từ bảng khác — tự dựng
    # từng đối tượng trả về ở đây.
    return [
        schemas.BaoCaoRa(
            bao_cao_id=bc.bao_cao_id,
            tin_dang_id=bc.tin_dang_id,
            ly_do=bc.ly_do,
            trang_thai=bc.trang_thai,
            gui_luc=bc.gui_luc,
            tieu_de_tin=bc.tin_dang.tieu_de if bc.tin_dang else None,
            nguoi_bao_cao=bc.nguoi_bao_cao,
            nguoi_bi_bao_cao=bc.tin_dang.nguoi_dung if bc.tin_dang else None,
        )
        for bc in danh_sach
    ]


@router.patch("/bao-cao/{bao_cao_id}/xu-ly", response_model=schemas.BaoCaoRa)
def xu_ly_bao_cao(bao_cao_id: int, db: Session = Depends(get_db)):
    bc = (
        db.query(models.BaoCaoViPham)
        .options(
            joinedload(models.BaoCaoViPham.nguoi_bao_cao),
            joinedload(models.BaoCaoViPham.tin_dang).joinedload(models.TinDang.nguoi_dung),
        )
        .filter(models.BaoCaoViPham.bao_cao_id == bao_cao_id)
        .first()
    )
    if not bc:
        raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo.")
    bc.trang_thai = "da_xu_ly"

    # Gửi kèm 1 ThongBao hệ thống cho người đã báo cáo — đúng dữ liệu mẫu
    # đang dùng ở ThongBao.jsx ("Báo cáo của bạn đã được xử lý")
    db.add(models.ThongBao(
        nguoi_nhan_id=bc.nguoi_bao_cao_id,
        tieu_de="Báo cáo của bạn đã được xử lý",
        noi_dung="Quản trị viên đã xem xét báo cáo vi phạm bạn gửi.",
        loai_thong_bao="HeThong",
    ))
    db.commit()
    db.refresh(bc)
    return schemas.BaoCaoRa(
        bao_cao_id=bc.bao_cao_id,
        tin_dang_id=bc.tin_dang_id,
        ly_do=bc.ly_do,
        trang_thai=bc.trang_thai,
        gui_luc=bc.gui_luc,
        tieu_de_tin=bc.tin_dang.tieu_de if bc.tin_dang else None,
        nguoi_bao_cao=bc.nguoi_bao_cao,
        nguoi_bi_bao_cao=bc.tin_dang.nguoi_dung if bc.tin_dang else None,
    )
