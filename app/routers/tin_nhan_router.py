"""
tin_nhan_router.py — UC-18: Nhắn tin trực tiếp (NhanTin.jsx)
-----------------------------------------------------------------
File NhanTin.jsx (frontend) có ghi chú: Backend "CHƯA có sẵn endpoint
liệt kê tất cả hội thoại của tôi" — endpoint /hoi-thoai-cua-toi bên
dưới chính là phần bổ sung đó.

    GET  /api/tin-nhan/hoi-thoai-cua-toi
         trả về danh sách hội thoại (gộp theo cặp tin_dang_id + người
         kia), kèm tin nhắn cuối cùng và số tin chưa đọc — đúng dữ
         liệu mà cột trái NhanTin.jsx cần.

    GET  /api/tin-nhan/hoi-thoai/{tin_dang_id}/{nguoi_kia_id}
         toàn bộ tin nhắn của 1 hội thoại cụ thể.

    POST /api/tin-nhan
         gửi 1 tin nhắn mới.

Vì Backend hiện xử lý theo kiểu REST thông thường (chưa dùng
WebSocket, xem mục 6.3 — Hướng phát triển), frontend nên gọi lại GET
định kỳ (setInterval) để cập nhật tin nhắn mới, đúng như đã ghi chú ở
đầu file NhanTin.jsx.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from ..database import get_db
from .. import models, schemas
from ..deps import lay_nguoi_dung_hien_tai

router = APIRouter(prefix="/api/tin-nhan", tags=["Tin nhắn"])


@router.get("/hoi-thoai-cua-toi")
def danh_sach_hoi_thoai_cua_toi(
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    toi_id = nguoi_dung_hien_tai.nguoi_dung_id

    tat_ca_tin_nhan = (
        db.query(models.TinNhan)
        .filter(or_(models.TinNhan.nguoi_gui_id == toi_id, models.TinNhan.nguoi_nhan_id == toi_id))
        .order_by(models.TinNhan.gui_luc.desc())
        .all()
    )

    # Gộp theo cặp (tin_dang_id, người còn lại) — mỗi cặp là 1 hội thoại
    hoi_thoai_theo_khoa = {}
    for tn in tat_ca_tin_nhan:
        nguoi_kia_id = tn.nguoi_nhan_id if tn.nguoi_gui_id == toi_id else tn.nguoi_gui_id
        khoa = (tn.tin_dang_id, nguoi_kia_id)

        if khoa not in hoi_thoai_theo_khoa:
            nguoi_kia = db.get(models.NguoiDung, nguoi_kia_id)
            tin_dang = db.get(models.TinDang, tn.tin_dang_id)
            hoi_thoai_theo_khoa[khoa] = {
                "tin_dang_id": tn.tin_dang_id,
                "tieu_de_tin": tin_dang.tieu_de if tin_dang else None,
                "nguoi_kia_id": nguoi_kia_id,
                "ten_nguoi_kia": nguoi_kia.ho_ten if nguoi_kia else "Người dùng",
                "tin_nhan_cuoi": tn.noi_dung,
                "cua_toi": tn.nguoi_gui_id == toi_id,
                "gui_luc": tn.gui_luc,
                "so_chua_doc": 0,
            }
        if tn.nguoi_nhan_id == toi_id and not tn.da_doc:
            hoi_thoai_theo_khoa[khoa]["so_chua_doc"] += 1

    return list(hoi_thoai_theo_khoa.values())


@router.get("/hoi-thoai/{tin_dang_id}/{nguoi_kia_id}", response_model=List[schemas.TinNhanRa])
def xem_hoi_thoai(
    tin_dang_id: int,
    nguoi_kia_id: int,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    toi_id = nguoi_dung_hien_tai.nguoi_dung_id

    tin_nhan = (
        db.query(models.TinNhan)
        .filter(
            models.TinNhan.tin_dang_id == tin_dang_id,
            or_(
                and_(models.TinNhan.nguoi_gui_id == toi_id, models.TinNhan.nguoi_nhan_id == nguoi_kia_id),
                and_(models.TinNhan.nguoi_gui_id == nguoi_kia_id, models.TinNhan.nguoi_nhan_id == toi_id),
            ),
        )
        .order_by(models.TinNhan.gui_luc.asc())
        .all()
    )

    # Đánh dấu các tin gửi TỚI tôi trong hội thoại này là đã đọc
    for tn in tin_nhan:
        if tn.nguoi_nhan_id == toi_id and not tn.da_doc:
            tn.da_doc = True
    db.commit()

    return tin_nhan


@router.post("", response_model=schemas.TinNhanRa, status_code=201)
def gui_tin_nhan(
    du_lieu: schemas.TinNhanTao,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    nguoi_nhan = db.get(models.NguoiDung, du_lieu.nguoi_nhan_id)
    if not nguoi_nhan:
        raise HTTPException(status_code=404, detail="Không tìm thấy người nhận.")

    tin_nhan_moi = models.TinNhan(
        tin_dang_id=du_lieu.tin_dang_id,
        nguoi_gui_id=nguoi_dung_hien_tai.nguoi_dung_id,
        nguoi_nhan_id=du_lieu.nguoi_nhan_id,
        noi_dung=du_lieu.noi_dung,
    )
    db.add(tin_nhan_moi)

    # Tự tạo 1 ThongBao loại "TinNhan" cho người nhận — đúng luồng đã mô
    # tả ở đầu file ThongBao.jsx (frontend): "tự động tạo khi có người
    # gửi tin nhắn".
    db.add(models.ThongBao(
        nguoi_nhan_id=du_lieu.nguoi_nhan_id,
        tieu_de="Bạn có tin nhắn mới",
        noi_dung=f"{nguoi_dung_hien_tai.ho_ten}: {du_lieu.noi_dung[:80]}",
        loai_thong_bao="TinNhan",
    ))

    db.commit()
    db.refresh(tin_nhan_moi)
    return tin_nhan_moi
