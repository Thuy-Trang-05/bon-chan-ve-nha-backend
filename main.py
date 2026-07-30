
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .database import Base, engine
from . import models
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

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

os.makedirs(os.path.join("static", "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.router)
app.include_router(nguoi_dung_router.router)
app.include_router(tin_dang_router.router)
app.include_router(tin_nhan_router.router)
app.include_router(thong_bao_router.router)
app.include_router(admin_router.router)

@app.get("/")
def kiem_tra_hoat_dong():
    return {"thong_diep": "API Bốn Chân Về Nhà đang chạy. Xem tài liệu tại /docs"}
