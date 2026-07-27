"""
deps.py — Dependency dùng chung: lấy người dùng hiện tại từ JWT
-----------------------------------------------------------------
Mỗi route cần đăng nhập (Đăng tin, Nhắn tin, Thông báo, Trang cá
nhân...) chỉ cần thêm tham số:

    nguoi_dung_hien_tai: NguoiDung = Depends(lay_nguoi_dung_hien_tai)

FastAPI sẽ tự đọc header "Authorization: Bearer <token>" do frontend
gửi lên, giải mã token (auth.giai_ma_jwt), tra database lấy đúng bản
ghi NguoiDung tương ứng — nếu token thiếu/sai/hết hạn thì tự trả lỗi
401 (Unauthorized), route bên trong không cần tự viết lại việc này.

yeu_cau_admin(): dùng thêm ở các route chỉ dành cho Admin (mục 3.1) —
kiểm tra vai_tro sau khi đã xác thực JWT thành công ở trên.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .auth import giai_ma_jwt
from . import models

# tokenUrl chỉ dùng để hiện ô "Authorize" trên trang tài liệu /docs,
# không ảnh hưởng gì tới luồng đăng nhập thật (POST /api/auth/dang-nhap).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/dang-nhap")


def lay_nguoi_dung_hien_tai(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.NguoiDung:
    loi_xac_thuc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    du_lieu = giai_ma_jwt(token)
    if du_lieu is None:
        raise loi_xac_thuc

    nguoi_dung_id = du_lieu.get("sub")
    if nguoi_dung_id is None:
        raise loi_xac_thuc

    nguoi_dung = db.get(models.NguoiDung, int(nguoi_dung_id))
    if nguoi_dung is None:
        raise loi_xac_thuc

    return nguoi_dung


def yeu_cau_admin(
    nguoi_dung_hien_tai: models.NguoiDung = Depends(lay_nguoi_dung_hien_tai),
) -> models.NguoiDung:
    if nguoi_dung_hien_tai.vai_tro != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có quyền truy cập chức năng này.",
        )
    return nguoi_dung_hien_tai
