from sqlalchemy import (
    Column, Integer, String, Text, Boolean, TIMESTAMP, DateTime,
    DECIMAL, ForeignKey, func,
)
from sqlalchemy.orm import relationship
from .database import Base


class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    nguoi_dung_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    mat_khau = Column(String(255), nullable=False)  # đã băm bằng bcrypt, xem app/auth.py
    ho_ten = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(15), nullable=True)
    anh_dai_dien = Column(String(255), nullable=True)
    vai_tro = Column(String(20), nullable=False, default="User")  # 'User' | 'Admin'
    dang_hoat_dong = Column(Boolean, nullable=False, default=True)  # False = tài khoản bị Admin khóa
    ngay_tao = Column(TIMESTAMP, server_default=func.now())

    tin_dang = relationship("TinDang", back_populates="nguoi_dung", cascade="all, delete-orphan")
    thu_cung = relationship("ThuCung", back_populates="nguoi_dung", cascade="all, delete-orphan")
    thong_bao = relationship("ThongBao", back_populates="nguoi_nhan", cascade="all, delete-orphan")


class LoaiThuCung(Base):
    __tablename__ = "loai_thu_cung"

    loai_id = Column(Integer, primary_key=True, autoincrement=True)
    ten_loai = Column(String(50), nullable=False)  # 'Chó' | 'Mèo' | 'Khác'

    thu_cung = relationship("ThuCung", back_populates="loai")


class ThuCung(Base):
    __tablename__ = "thu_cung"

    thu_cung_id = Column(Integer, primary_key=True, autoincrement=True)
    ten_thu_cung = Column(String(50), nullable=True)
    loai_id = Column(Integer, ForeignKey("loai_thu_cung.loai_id"), nullable=False)
    giong = Column(String(50), nullable=True)
    gioi_tinh = Column(String(10), nullable=True)  # 'Đực' | 'Cái' | 'Không rõ'
    mau_sac = Column(String(50), nullable=True)
    dac_diem = Column(Text, nullable=True)
    nguoi_dung_id = Column(Integer, ForeignKey("nguoi_dung.nguoi_dung_id"), nullable=False)

    loai = relationship("LoaiThuCung", back_populates="thu_cung")
    nguoi_dung = relationship("NguoiDung", back_populates="thu_cung")
    tin_dang = relationship("TinDang", back_populates="thu_cung")


class TinDang(Base):
    __tablename__ = "tin_dang"

    tin_dang_id = Column(Integer, primary_key=True, autoincrement=True)
    nguoi_dung_id = Column(Integer, ForeignKey("nguoi_dung.nguoi_dung_id"), nullable=False)
    thu_cung_id = Column(Integer, ForeignKey("thu_cung.thu_cung_id"), nullable=True)
    loai_tin = Column(String(20), nullable=False)  # 'Lạc mất' | 'Tìm thấy'
    tieu_de = Column(String(150), nullable=False)
    mo_ta = Column(Text, nullable=True)
    khu_vuc = Column(String(100), nullable=True)
    # 'dang_hien_thi' (mặc định) | 'da_giai_quyet' (UC-13) | 'da_an' (UC-16)
    trang_thai = Column(String(20), nullable=False, default="dang_hien_thi")
    ngay_dang = Column(TIMESTAMP, server_default=func.now())
    vi_do = Column(DECIMAL(10, 8), nullable=True)
    kinh_do = Column(DECIMAL(11, 8), nullable=True)

    nguoi_dung = relationship("NguoiDung", back_populates="tin_dang")
    thu_cung = relationship("ThuCung", back_populates="tin_dang")
    hinh_anh = relationship("HinhAnh", back_populates="tin_dang", cascade="all, delete-orphan")
    tin_nhan = relationship("TinNhan", back_populates="tin_dang", cascade="all, delete-orphan")
    bao_cao = relationship("BaoCaoViPham", back_populates="tin_dang", cascade="all, delete-orphan")


class HinhAnh(Base):
    __tablename__ = "hinh_anh"

    hinh_anh_id = Column(Integer, primary_key=True, autoincrement=True)
    tin_dang_id = Column(Integer, ForeignKey("tin_dang.tin_dang_id"), nullable=False)
    duong_dan = Column(String(255), nullable=False)
    hash_anh = Column(String(64), nullable=True) 
    la_anh_chinh = Column(Boolean, default=False)

    tin_dang = relationship("TinDang", back_populates="hinh_anh")


class TinNhan(Base):
    __tablename__ = "tin_nhan"

    tin_nhan_id = Column(Integer, primary_key=True, autoincrement=True)
    tin_dang_id = Column(Integer, ForeignKey("tin_dang.tin_dang_id"), nullable=False)
    nguoi_gui_id = Column(Integer, ForeignKey("nguoi_dung.nguoi_dung_id"), nullable=False)
    nguoi_nhan_id = Column(Integer, ForeignKey("nguoi_dung.nguoi_dung_id"), nullable=False)
    noi_dung = Column(Text, nullable=False)
    da_doc = Column(Boolean, default=False)
    gui_luc = Column(DateTime, server_default=func.now())

    tin_dang = relationship("TinDang", back_populates="tin_nhan")
    nguoi_gui = relationship("NguoiDung", foreign_keys=[nguoi_gui_id])
    nguoi_nhan = relationship("NguoiDung", foreign_keys=[nguoi_nhan_id])


class BaoCaoViPham(Base):
    __tablename__ = "bao_cao_vi_pham"

    bao_cao_id = Column(Integer, primary_key=True, autoincrement=True)
    tin_dang_id = Column(Integer, ForeignKey("tin_dang.tin_dang_id"), nullable=False)
    nguoi_bao_cao_id = Column(Integer, ForeignKey("nguoi_dung.nguoi_dung_id"), nullable=False)
    ly_do = Column(Text, nullable=False)
    trang_thai = Column(String(20), nullable=False, default="cho_xu_ly")  # 'cho_xu_ly' | 'da_xu_ly'
    gui_luc = Column(DateTime, server_default=func.now())

    tin_dang = relationship("TinDang", back_populates="bao_cao")
    nguoi_bao_cao = relationship("NguoiDung")


class ThongBao(Base):
    __tablename__ = "thong_bao"

    thong_bao_id = Column(Integer, primary_key=True, autoincrement=True)
    nguoi_nhan_id = Column(Integer, ForeignKey("nguoi_dung.nguoi_dung_id"), nullable=False)
    tieu_de = Column(String(100), nullable=False)
    noi_dung = Column(Text, nullable=True)
    loai_thong_bao = Column(String(30), nullable=False, default="HeThong")  # 'TinNhan' | 'HeThong'
    da_doc = Column(Boolean, default=False)
    ngay_tao = Column(TIMESTAMP, server_default=func.now())

    nguoi_nhan = relationship("NguoiDung", back_populates="thong_bao")
