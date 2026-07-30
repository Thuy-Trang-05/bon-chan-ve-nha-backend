
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class DangKyTao(BaseModel):
    ho_ten: str = Field(min_length=1, max_length=100)
    email: EmailStr
    mat_khau: str = Field(min_length=6, max_length=255)
    so_dien_thoai: Optional[str] = None

class DangNhapTao(BaseModel):
    email: EmailStr
    mat_khau: str

class NguoiDungRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nguoi_dung_id: int
    ho_ten: str
    email: EmailStr
    so_dien_thoai: Optional[str] = None
    anh_dai_dien: Optional[str] = None
    vai_tro: str
    dang_hoat_dong: bool
    ngay_tao: datetime

class NguoiDungCapNhat(BaseModel):
    ho_ten: Optional[str] = None
    so_dien_thoai: Optional[str] = None

class TokenRa(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nguoi_dung: NguoiDungRa

class HinhAnhRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hinh_anh_id: int
    duong_dan: str
    la_anh_chinh: bool

class LoaiThuCungRaGon(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ten_loai: str

class ThuCungRaGon(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ten_thu_cung: Optional[str] = None
    loai: LoaiThuCungRaGon

class TinDangTao(BaseModel):
    loai_tin: str = Field(description="'Lạc mất' hoặc 'Tìm thấy'")
    ten_thu_cung: Optional[str] = None
    loai_thu_cung: str = Field(description="Tên loại: 'Chó' | 'Mèo' | 'Khác'")
    mo_ta: Optional[str] = None
    khu_vuc: Optional[str] = None
    vi_do: Optional[float] = None
    kinh_do: Optional[float] = None

class TinDangCapNhatTrangThai(BaseModel):
    trang_thai: str = Field(description="'dang_hien_thi' | 'da_giai_quyet' | 'da_an'")

class TinDangCapNhat(BaseModel):
    tieu_de: Optional[str] = None
    mo_ta: Optional[str] = None
    khu_vuc: Optional[str] = None

class NguoiDangRaGon(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nguoi_dung_id: int
    ho_ten: str
    so_dien_thoai: Optional[str] = None

class TinDangRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tin_dang_id: int
    loai_tin: str
    tieu_de: str
    mo_ta: Optional[str] = None
    khu_vuc: Optional[str] = None
    trang_thai: str
    ngay_dang: datetime
    vi_do: Optional[float] = None
    kinh_do: Optional[float] = None
    nguoi_dung: NguoiDangRaGon
    hinh_anh: List[HinhAnhRa] = []
    thu_cung: Optional[ThuCungRaGon] = None

class TinNhanTao(BaseModel):
    tin_dang_id: int
    nguoi_nhan_id: int
    noi_dung: str = Field(min_length=1)

class TinNhanRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tin_nhan_id: int
    tin_dang_id: int
    nguoi_gui_id: int
    nguoi_nhan_id: int
    noi_dung: str
    da_doc: bool
    gui_luc: datetime

class BaoCaoTao(BaseModel):
    ly_do: str = Field(min_length=1)

class BaoCaoRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bao_cao_id: int
    tin_dang_id: int
    ly_do: str
    trang_thai: str
    gui_luc: datetime
    tieu_de_tin: Optional[str] = None
    nguoi_bao_cao: Optional[NguoiDangRaGon] = None
    nguoi_bi_bao_cao: Optional[NguoiDangRaGon] = None

class ThongBaoRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    thong_bao_id: int
    tieu_de: str
    noi_dung: Optional[str] = None
    loai_thong_bao: str
    da_doc: bool
    ngay_tao: datetime
