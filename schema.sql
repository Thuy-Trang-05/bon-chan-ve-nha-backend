CREATE DATABASE IF NOT EXISTS bon_chan_ve_nha
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE bon_chan_ve_nha;

-- Bảng 1: NguoiDung
CREATE TABLE IF NOT EXISTS nguoi_dung (
  nguoi_dung_id   INT AUTO_INCREMENT PRIMARY KEY,
  email           VARCHAR(100) NOT NULL UNIQUE,
  mat_khau        VARCHAR(255) NOT NULL,
  ho_ten          VARCHAR(100) NOT NULL,
  so_dien_thoai   VARCHAR(15),
  anh_dai_dien    VARCHAR(255),
  vai_tro         VARCHAR(20) NOT NULL DEFAULT 'User',
  dang_hoat_dong  BOOLEAN NOT NULL DEFAULT TRUE,
  ngay_tao        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng 3: LoaiThuCung 
CREATE TABLE IF NOT EXISTS loai_thu_cung (
  loai_id     INT AUTO_INCREMENT PRIMARY KEY,
  ten_loai    VARCHAR(50) NOT NULL
);

-- Bảng 2: ThuCung
CREATE TABLE IF NOT EXISTS thu_cung (
  thu_cung_id     INT AUTO_INCREMENT PRIMARY KEY,
  ten_thu_cung    VARCHAR(50),
  loai_id         INT NOT NULL,
  giong           VARCHAR(50),
  gioi_tinh       VARCHAR(10),
  mau_sac         VARCHAR(50),
  dac_diem        TEXT,
  nguoi_dung_id   INT NOT NULL,
  FOREIGN KEY (loai_id) REFERENCES loai_thu_cung(loai_id),
  FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE
);

-- Bảng 4: TinDang
CREATE TABLE IF NOT EXISTS tin_dang (
  tin_dang_id     INT AUTO_INCREMENT PRIMARY KEY,
  nguoi_dung_id   INT NOT NULL,
  thu_cung_id     INT,
  loai_tin        VARCHAR(20) NOT NULL,
  tieu_de         VARCHAR(150) NOT NULL,
  mo_ta           TEXT,
  khu_vuc         VARCHAR(100),
  trang_thai      VARCHAR(20) NOT NULL DEFAULT 'dang_hien_thi',
  ngay_dang       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  vi_do           DECIMAL(10,8),
  kinh_do         DECIMAL(11,8),
  FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE,
  FOREIGN KEY (thu_cung_id) REFERENCES thu_cung(thu_cung_id)
);

-- Bảng 5: HinhAnh
CREATE TABLE IF NOT EXISTS hinh_anh (
  hinh_anh_id     INT AUTO_INCREMENT PRIMARY KEY,
  tin_dang_id     INT NOT NULL,
  duong_dan       VARCHAR(255) NOT NULL,
  hash_anh        VARCHAR(64),
  la_anh_chinh    BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (tin_dang_id) REFERENCES tin_dang(tin_dang_id) ON DELETE CASCADE
);

-- Bảng 6: TinNhan
CREATE TABLE IF NOT EXISTS tin_nhan (
  tin_nhan_id     INT AUTO_INCREMENT PRIMARY KEY,
  tin_dang_id     INT NOT NULL,
  nguoi_gui_id    INT NOT NULL,
  nguoi_nhan_id   INT NOT NULL,
  noi_dung        TEXT NOT NULL,
  da_doc          BOOLEAN DEFAULT FALSE,
  gui_luc         DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tin_dang_id) REFERENCES tin_dang(tin_dang_id) ON DELETE CASCADE,
  FOREIGN KEY (nguoi_gui_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE,
  FOREIGN KEY (nguoi_nhan_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE
);

-- Bảng 7: BaoCaoViPham
CREATE TABLE IF NOT EXISTS bao_cao_vi_pham (
  bao_cao_id          INT AUTO_INCREMENT PRIMARY KEY,
  tin_dang_id         INT NOT NULL,
  nguoi_bao_cao_id    INT NOT NULL,
  ly_do               TEXT NOT NULL,
  trang_thai          VARCHAR(20) NOT NULL DEFAULT 'cho_xu_ly',
  gui_luc             DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tin_dang_id) REFERENCES tin_dang(tin_dang_id) ON DELETE CASCADE,
  FOREIGN KEY (nguoi_bao_cao_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE
);

-- Bảng 8: ThongBao
CREATE TABLE IF NOT EXISTS thong_bao (
  thong_bao_id    INT AUTO_INCREMENT PRIMARY KEY,
  nguoi_nhan_id   INT NOT NULL,
  tieu_de         VARCHAR(100) NOT NULL,
  noi_dung        TEXT,
  loai_thong_bao  VARCHAR(30) NOT NULL DEFAULT 'HeThong',
  da_doc          BOOLEAN DEFAULT FALSE,
  ngay_tao        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (nguoi_nhan_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE
);

-- ---- Dữ liệu mẫu ban đầu: 3 loại thú cưng cố định ----
INSERT INTO loai_thu_cung (ten_loai)
SELECT * FROM (SELECT 'Chó' AS ten_loai) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM loai_thu_cung WHERE ten_loai = 'Chó');

INSERT INTO loai_thu_cung (ten_loai)
SELECT * FROM (SELECT 'Mèo' AS ten_loai) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM loai_thu_cung WHERE ten_loai = 'Mèo');

INSERT INTO loai_thu_cung (ten_loai)
SELECT * FROM (SELECT 'Khác' AS ten_loai) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM loai_thu_cung WHERE ten_loai = 'Khác');
