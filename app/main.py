"""
main.py — Điểm khởi động ứng dụng FastAPI (đúng mục 4.2.3 tiểu luận:
"main.py là điểm khởi tạo ứng dụng FastAPI, khai báo các router và
cấu hình CORS")
-----------------------------------------------------------------
Chạy thử:  uvicorn app.main:app --reload
Tài liệu API tự sinh (Swagger UI):  http://localhost:8000/docs
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .database import Base, engine
from . import models  # noqa: F401 — import để SQLAlchemy biết hết các bảng trước khi create_all
from .routers import (
    auth_router,
    nguoi_dung_router,
    tin_dang_router,
    tin_nhan_router,
    thong_bao_router,
    admin_router,
)

load_dotenv()

app = FastAPI(
    title="Bốn Chân Về Nhà — API",
    description="Backend hỗ trợ tìm kiếm và kết nối thú cưng thất lạc tại Huế.",
    version="1.0.0",
)

# ---- CORS: cho phép frontend (chạy ở cổng khác, ví dụ 5173) gọi API ----
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Tự tạo bảng nếu chưa tồn tại (tiện lúc phát triển; khi làm đồ án
# nộp báo cáo, khuyến khích tạo bảng bằng schema.sql qua MySQL Workbench
# như đã mô tả ở mục 2.3.3 để chủ động kiểm soát ERD hơn) ----
Base.metadata.create_all(bind=engine)

# ---- Phục vụ ảnh đã tải lên tại /static/uploads/... ----
os.makedirs(os.path.join("static", "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---- Gắn các router ----
app.include_router(auth_router.router)
app.include_router(nguoi_dung_router.router)
app.include_router(tin_dang_router.router)
app.include_router(tin_nhan_router.router)
app.include_router(thong_bao_router.router)
app.include_router(admin_router.router)


@app.get("/")
def kiem_tra_hoat_dong():
    return {"thong_diep": "API Bốn Chân Về Nhà đang chạy. Xem tài liệu tại /docs"}
