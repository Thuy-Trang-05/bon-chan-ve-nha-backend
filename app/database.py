"""
database.py — Kết nối MySQL qua SQLAlchemy
-----------------------------------------------------------------
Đúng như đã chọn ở mục 2.3.3 tiểu luận: MySQL kết hợp SQLAlchemy làm
ORM (Object-Relational Mapping) để FastAPI thao tác với database bằng
đối tượng Python thay vì viết SQL thuần.

engine: đại diện cho kết nối tới MySQL (đọc từ biến môi trường
DATABASE_URL trong file .env, xem .env.example).

SessionLocal: mỗi request API sẽ mở 1 "phiên làm việc" (Session) riêng
với database, dùng xong đóng lại — tránh giữ kết nối treo.

get_db(): hàm được các router gọi qua Depends(get_db) để lấy 1 Session
sẵn sàng dùng, tự đóng lại sau khi request xử lý xong (kể cả khi có
lỗi), nhờ khối try/finally.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:matkhau@localhost:3306/bon_chan_ve_nha",
)

# pool_pre_ping=True: tự kiểm tra kết nối còn sống trước khi dùng —
# tránh lỗi "MySQL server has gone away" khi kết nối bị treo quá lâu.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
