
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..deps import lay_nguoi_dung_hien_tai

router = APIRouter(prefix="/api/thong-bao", tags=["Thông báo"])

@router.get("", response_model=List[schemas.ThongBaoRa])
def danh_sach_thong_bao(
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.ThongBao)
        .filter(models.ThongBao.nguoi_nhan_id == nguoi_dung_hien_tai.nguoi_dung_id)
        .order_by(models.ThongBao.ngay_tao.desc())
        .all()
    )

@router.patch("/{thong_bao_id}/da-doc", response_model=schemas.ThongBaoRa)
def danh_dau_da_doc(
    thong_bao_id: int,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    tb = db.get(models.ThongBao, thong_bao_id)
    if not tb or tb.nguoi_nhan_id != nguoi_dung_hien_tai.nguoi_dung_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo.")
    tb.da_doc = True
    db.commit()
    db.refresh(tb)
    return tb

@router.patch("/danh-dau-tat-ca-da-doc")
def danh_dau_tat_ca_da_doc(
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    (
        db.query(models.ThongBao)
        .filter(
            models.ThongBao.nguoi_nhan_id == nguoi_dung_hien_tai.nguoi_dung_id,
            models.ThongBao.da_doc == False,
        )
        .update({"da_doc": True})
    )
    db.commit()
    return {"thanh_cong": True}

@router.delete("/{thong_bao_id}", status_code=204)
def xoa_thong_bao(
    thong_bao_id: int,
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
    db: Session = Depends(get_db),
):
    tb = db.get(models.ThongBao, thong_bao_id)
    if not tb or tb.nguoi_nhan_id != nguoi_dung_hien_tai.nguoi_dung_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo.")
    db.delete(tb)
    db.commit()
    return None
