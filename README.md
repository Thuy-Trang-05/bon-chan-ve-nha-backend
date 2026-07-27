# Backend — Bốn Chân Về Nhà

API viết bằng Python (FastAPI) + MySQL, đúng công nghệ đã chọn ở mục 2.3
tiểu luận. Thư mục này **tách biệt hoàn toàn** với thư mục frontend React
(`bon-chan-ve-nha`) — 2 project chạy song song, nói chuyện với nhau qua API.

## Cấu trúc thư mục

```
backend/
├── requirements.txt      danh sách thư viện Python cần cài
├── .env.example           mẫu file cấu hình (copy thành .env)
├── schema.sql              script tạo database bằng tay (MySQL Workbench)
└── app/
    ├── main.py             điểm khởi động, gắn router + CORS
    ├── database.py         kết nối MySQL
    ├── models.py           8 bảng dữ liệu (SQLAlchemy)
    ├── schemas.py          kiểm tra dữ liệu vào/ra (Pydantic)
    ├── auth.py             mã hóa mật khẩu + JWT
    ├── deps.py             kiểm tra "ai đang đăng nhập"
    └── routers/            các nhóm API, chia theo chức năng
```

## Bước 1 — Cài Python (nếu máy chưa có)

Mở Terminal, gõ:
```bash
python3 --version
```
Nếu hiện số phiên bản (khuyến khích 3.10 trở lên) là được. Nếu báo lỗi,
tải tại https://www.python.org/downloads/ (bản macOS installer), cài như
app bình thường.

## Bước 2 — Cài MySQL (nếu máy chưa có)

Cách dễ nhất trên Mac: cài **MySQL Community Server** tại
https://dev.mysql.com/downloads/mysql/ (chọn bản macOS, tải file `.dmg`).
Lúc cài sẽ được yêu cầu đặt **mật khẩu root** — nhớ kỹ mật khẩu này, sẽ
cần dùng lại ở Bước 5.

Tiện thể cài luôn **MySQL Workbench** (công cụ xem CSDL trực quan, đúng
như tiểu luận có nhắc) tại https://dev.mysql.com/downloads/workbench/.

## Bước 3 — Tạo môi trường ảo Python và cài thư viện

Trong Terminal, `cd` vào đúng thư mục `backend` này (thư mục chứa file
`requirements.txt`), rồi:

```bash
python3 -m venv venv
source venv/bin/activate
```

(Sau lệnh `source`, đầu dòng Terminal sẽ hiện thêm chữ `(venv)` — nghĩa
là đã vào đúng "môi trường ảo", các thư viện cài sau đây sẽ không lẫn
với các project Python khác trên máy.)

```bash
pip install -r requirements.txt
```

Chờ chạy xong (có thể mất 1–2 phút).

> Từ giờ về sau, mỗi lần mở Terminal mới để làm việc với backend, phải
> gõ lại `source venv/bin/activate` trước, rồi mới chạy các lệnh `python`/
> `uvicorn` — nếu không sẽ báo lỗi "No module named fastapi".

## Bước 4 — Tạo file cấu hình `.env`

```bash
cp .env.example .env
```

Mở file `.env` vừa tạo bằng VS Code, sửa dòng `DATABASE_URL`, thay
`matkhau_cua_ban` bằng đúng mật khẩu root MySQL đã đặt ở Bước 2:

```
DATABASE_URL=mysql+pymysql://root:MAT_KHAU_THAT_CUA_BAN@localhost:3306/bon_chan_ve_nha
```

## Bước 5 — Tạo database

Mở **MySQL Workbench**, kết nối vào MySQL (thường sẵn 1 kết nối tên
"Local instance MySQL", double-click vào, nhập mật khẩu root).

Vào **File → Open SQL Script**, chọn file `schema.sql` trong thư mục
`backend` này, rồi bấm nút hình tia sét ⚡ (Execute) ở thanh công cụ để
chạy toàn bộ — lệnh này tự tạo database `bon_chan_ve_nha` và 8 bảng.

## Bước 6 — Chạy thử server

Quay lại Terminal (đảm bảo vẫn thấy `(venv)` ở đầu dòng, nếu không thì
`source venv/bin/activate` lại), gõ:

```bash
uvicorn app.main:app --reload
```

Thấy dòng `Uvicorn running on http://127.0.0.1:8000` là thành công. Mở
trình duyệt vào **http://localhost:8000/docs** — đây là trang tài liệu
API tự sinh (Swagger UI) của FastAPI, liệt kê toàn bộ endpoint, có thể
bấm thử trực tiếp (Try it out) mà không cần viết code frontend.

## Bước 7 — Nối Frontend vào Backend thật

Trong project React (`bon-chan-ve-nha`), các trang hiện đang dùng dữ
liệu mẫu viết cứng (`DANH_SACH_..._MAU`). Bước tiếp theo (nếu bạn muốn)
là thay từng đoạn đó bằng lệnh gọi API thật tới `http://localhost:8000`,
đúng theo các ghi chú "Trong dự án thật: gọi POST/GET..." đã có sẵn
trong từng file `.jsx`.

Đây là phần việc lớn tiếp theo — báo tôi khi bạn chạy xong Bước 6 để
mình bắt đầu nối từng trang một, giống cách mình đã làm với React Router
trước đây.
