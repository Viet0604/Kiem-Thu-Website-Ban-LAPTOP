-- =============================================
-- DATABASE: laptop_store
-- Website Bán Laptop - Kiểm Thử Phần Mềm
-- =============================================

CREATE DATABASE IF NOT EXISTS laptop_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE laptop_store;

-- =============================================
-- BẢNG: users - Tài khoản người dùng
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) DEFAULT NULL,
    address TEXT DEFAULT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    is_locked TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- BẢNG: products - Sản phẩm laptop
-- =============================================
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    cpu VARCHAR(100) NOT NULL,
    ram VARCHAR(20) NOT NULL,
    storage VARCHAR(50) NOT NULL,
    screen_size VARCHAR(100) NOT NULL,
    gpu VARCHAR(100) DEFAULT NULL,
    price DECIMAL(15,0) NOT NULL,
    stock INT DEFAULT 0,
    image VARCHAR(255) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- BẢNG: orders - Đơn hàng
-- =============================================
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    receiver_name VARCHAR(100) NOT NULL,
    receiver_phone VARCHAR(15) NOT NULL,
    receiver_address TEXT NOT NULL,
    payment_method ENUM('cod', 'bank_transfer', 'momo') DEFAULT 'cod',
    total_amount DECIMAL(15,0) NOT NULL DEFAULT 0,
    status ENUM('pending', 'processing', 'shipping', 'delivered', 'cancelled') DEFAULT 'pending',
    note TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- BẢNG: order_details - Chi tiết đơn hàng
-- =============================================
CREATE TABLE IF NOT EXISTS order_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    price DECIMAL(15,0) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================
-- UPGRADE V2: Quản lý Nhà cung cấp & Kho
-- =============================================

-- =============================================
-- BẢNG: suppliers - Nhà cung cấp
-- =============================================
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100) DEFAULT NULL,
    phone VARCHAR(15) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    address TEXT DEFAULT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Thêm cột supplier_id vào products (nếu chưa có)
-- =============================================
-- ALTER TABLE products ADD COLUMN supplier_id INT DEFAULT NULL;
-- ALTER TABLE products ADD FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL;

-- =============================================
-- BẢNG: inventory_logs - Lịch sử nhập/xuất kho
-- =============================================
CREATE TABLE IF NOT EXISTS inventory_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    supplier_id INT DEFAULT NULL,
    type ENUM('import', 'export', 'adjustment') NOT NULL,
    quantity INT NOT NULL,
    note TEXT DEFAULT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================
-- DỮ LIỆU MẪU: Tài khoản admin
-- Mật khẩu: admin123 (đã hash bằng password_hash)
-- =============================================
INSERT INTO users (fullname, email, phone, address, password, role) VALUES
('Administrator', 'admin@laptopstore.vn', '0901234567', 'Hà Nội, Việt Nam', '$2y$10$wnI9UfvP0zt7wkK5wa72l.Ti4Cyib00cq6kgtWh773tgEQ7lQvV5.', 'admin');

-- Tài khoản user test: password = user123
INSERT INTO users (fullname, email, phone, address, password, role) VALUES
('Nguyễn Văn A', 'user@gmail.com', '0912345678', '123 Nguyễn Huệ, Q.1, TP.HCM', '$2y$10$IF6Bv.MdswKP3V0HichWYe5zsxtLCRFiP9uGm4KTeHTc6lSCuFTQq', 'user');

-- =============================================
-- DỮ LIỆU MẪU: Sản phẩm laptop (15 sản phẩm)
-- =============================================
INSERT INTO products (name, brand, cpu, ram, storage, screen_size, gpu, price, stock, image, description) VALUES

-- ASUS
('ASUS ROG Strix G16 2024', 'ASUS', 'Intel Core i9-14900HX', '16GB DDR5', '512GB SSD NVMe', '16 inch QHD+', 'NVIDIA RTX 4060 8GB', 32990000, 15, 'asus_rog_strix_g16.jpg', 'Laptop gaming cao cấp với hiệu năng mạnh mẽ, màn hình 240Hz, bàn phím RGB, tản nhiệt tiên tiến. Phù hợp cho game thủ và nhà sáng tạo nội dung.'),

('ASUS VivoBook 15 OLED', 'ASUS', 'Intel Core i5-13500H', '16GB DDR4', '512GB SSD NVMe', '15.6 inch FHD OLED', 'Intel Iris Xe', 16990000, 25, 'asus_vivobook_15.jpg', 'Laptop mỏng nhẹ với màn hình OLED sắc nét, pin lâu, thiết kế hiện đại. Lý tưởng cho sinh viên và dân văn phòng.'),

('ASUS ZenBook 14 OLED', 'ASUS', 'AMD Ryzen 7 7840U', '16GB LPDDR5', '512GB SSD NVMe', '14 inch 2.8K OLED', 'AMD Radeon 780M', 24990000, 10, 'asus_zenbook_14.jpg', 'Ultrabook cao cấp siêu mỏng nhẹ chỉ 1.2kg, màn hình OLED 2.8K, hiệu năng xử lý đa nhiệm vượt trội.'),

-- DELL
('Dell XPS 15 9530', 'Dell', 'Intel Core i7-13700H', '16GB DDR5', '512GB SSD NVMe', '15.6 inch 3.5K OLED', 'NVIDIA RTX 4050 6GB', 38990000, 8, 'dell_xps_15.jpg', 'Laptop premium với thiết kế InfinityEdge, màn hình 3.5K OLED tuyệt đẹp, vỏ nhôm CNC cao cấp. Dành cho chuyên gia sáng tạo.'),

('Dell Inspiron 15 3530', 'Dell', 'Intel Core i5-1335U', '8GB DDR4', '256GB SSD NVMe', '15.6 inch FHD', 'Intel Iris Xe', 12990000, 30, 'dell_inspiron_15.jpg', 'Laptop phổ thông đáng tin cậy, hiệu năng ổn định cho công việc văn phòng và học tập hàng ngày.'),

('Dell Gaming G15 5530', 'Dell', 'Intel Core i7-13650HX', '16GB DDR5', '512GB SSD NVMe', '15.6 inch FHD 165Hz', 'NVIDIA RTX 4060 8GB', 27990000, 12, 'dell_gaming_g15.jpg', 'Laptop gaming mạnh mẽ với card đồ họa RTX 4060, màn hình tốc độ cao 165Hz, hệ thống tản nhiệt kép hiệu quả.'),

-- HP
('HP Pavilion 15-eg3000', 'HP', 'Intel Core i5-1340P', '8GB DDR4', '512GB SSD NVMe', '15.6 inch FHD IPS', 'Intel Iris Xe', 14990000, 20, 'hp_pavilion_15.jpg', 'Laptop thanh lịch với thiết kế mỏng nhẹ, hiệu năng đủ dùng cho công việc và giải trí, pin sử dụng cả ngày.'),

('HP Envy x360 15', 'HP', 'AMD Ryzen 7 7730U', '16GB DDR4', '512GB SSD NVMe', '15.6 inch FHD IPS Touch', 'AMD Radeon Graphics', 21990000, 10, 'hp_envy_x360.jpg', 'Laptop 2-in-1 xoay gập 360 độ, màn hình cảm ứng, bút stylus đi kèm. Linh hoạt cho công việc và sáng tạo.'),

-- LENOVO
('Lenovo ThinkPad X1 Carbon Gen 11', 'Lenovo', 'Intel Core i7-1365U', '16GB LPDDR5', '512GB SSD NVMe', '14 inch 2.8K OLED', 'Intel Iris Xe', 35990000, 7, 'lenovo_thinkpad_x1.jpg', 'Laptop doanh nhân hàng đầu, siêu bền theo chuẩn quân đội MIL-STD-810H, bảo mật vân tay và IR camera.'),

('Lenovo IdeaPad Slim 5 14', 'Lenovo', 'AMD Ryzen 5 7530U', '8GB DDR4', '512GB SSD NVMe', '14 inch FHD IPS', 'AMD Radeon Graphics', 13490000, 22, 'lenovo_ideapad_slim5.jpg', 'Laptop mỏng nhẹ với hiệu năng AMD Ryzen 5, pin 12 tiếng, phù hợp cho sinh viên và người đi làm.'),

('Lenovo Legion 5 Pro', 'Lenovo', 'AMD Ryzen 7 7745HX', '16GB DDR5', '1TB SSD NVMe', '16 inch WQXGA 165Hz', 'NVIDIA RTX 4070 8GB', 34990000, 9, 'lenovo_legion_5pro.jpg', 'Laptop gaming hiệu năng cao với RTX 4070, màn hình WQXGA 165Hz, tản nhiệt ColdFront 5.0 giữ mát khi chiến game.'),

-- ACER
('Acer Aspire 5 A515-58', 'Acer', 'Intel Core i5-13420H', '8GB DDR4', '512GB SSD NVMe', '15.6 inch FHD IPS', 'Intel UHD Graphics', 11990000, 35, 'acer_aspire_5.jpg', 'Laptop giá tốt với cấu hình mạnh trong phân khúc, thiết kế gọn nhẹ, phù hợp cho sinh viên và văn phòng.'),

('Acer Nitro V ANV15-51', 'Acer', 'Intel Core i5-13420H', '16GB DDR5', '512GB SSD NVMe', '15.6 inch FHD 144Hz', 'NVIDIA RTX 4050 6GB', 19990000, 18, 'acer_nitro_v.jpg', 'Laptop gaming entry-level với RTX 4050, màn hình 144Hz mượt mà, tản nhiệt kép quạt lớn.'),

-- MSI
('MSI Modern 14 C13M', 'MSI', 'Intel Core i5-1335U', '8GB DDR4', '512GB SSD NVMe', '14 inch FHD IPS', 'Intel Iris Xe', 12490000, 20, 'msi_modern_14.jpg', 'Laptop văn phòng mỏng nhẹ chỉ 1.4kg, thiết kế chuyên nghiệp, hiệu năng ổn định cho công việc hàng ngày.'),

-- APPLE
('MacBook Air M3 2024', 'Apple', 'Apple M3 8-core', '8GB Unified', '256GB SSD', '13.6 inch Liquid Retina', 'Apple M3 10-core GPU', 27490000, 15, 'macbook_air_m3.jpg', 'MacBook Air với chip M3 mới nhất, thiết kế fanless siêu mỏng, pin 18 tiếng, hiệu năng vượt trội cho mọi tác vụ.');


-- =============================================
-- DỮ LIỆU MẪU: Nhà cung cấp
-- =============================================
INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES
('Công ty TNHH Phân phối ASUS Việt Nam', 'Nguyễn Minh Tuấn', '0281234567', 'sales@asus.vn', '123 Nguyễn Du, Q.1, TP.HCM'),
('Dell Technologies Vietnam', 'Trần Văn Hùng', '0287654321', 'sales@dell.vn', '456 Lê Lợi, Q.1, TP.HCM'),
('HP Vietnam Distribution', 'Lê Thị Hoa', '0289876543', 'sales@hp.vn', '789 Trần Hưng Đạo, Q.5, TP.HCM'),
('Lenovo Vietnam Co., Ltd', 'Phạm Đức Anh', '0282345678', 'sales@lenovo.vn', '101 Điện Biên Phủ, Q.Bình Thạnh, TP.HCM'),
('Acer Vietnam Distribution', 'Hoàng Thanh Mai', '0283456789', 'sales@acer.vn', '202 Cách Mạng Tháng 8, Q.3, TP.HCM'),
('MSI Vietnam', 'Vũ Quang Huy', '0284567890', 'sales@msi.vn', '303 Võ Văn Tần, Q.3, TP.HCM'),
('Apple Authorized Vietnam', 'Đặng Thị Ngọc', '0285678901', 'sales@apple.vn', '404 Đồng Khởi, Q.1, TP.HCM');
