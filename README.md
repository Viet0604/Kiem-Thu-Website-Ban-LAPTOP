# Website Bán Laptop - Báo Cáo Bài Tập Lớn Kiểm Thử Phần Mềm

Đây là dự án Website bán Laptop trực tuyến được xây dựng bằng **Flask (Python)** và hệ quản trị cơ sở dữ liệu **MySQL**. Dự án được phát triển nhằm phục vụ cho Bài Tập Lớn môn Kiểm Thử Phần Mềm, tập trung vào việc áp dụng các kỹ thuật kiểm thử tự động (Unit Test, Integration Test, System Test) trên một hệ thống hoàn chỉnh.

Toàn bộ 42 kịch bản kiểm thử (Test Cases) đã được lập trình tự động bằng `pytest` kết hợp với kỹ thuật giả lập dữ liệu `unittest.mock`, đạt tỷ lệ Pass 100%.

---

## 🚀 Các Tính Năng Của Hệ Thống

Dự án bao gồm 5 module chức năng cốt lõi đã được kiểm thử:
- **Xác thực (Authentication)**: Đăng ký, đăng nhập, phân quyền (User/Admin), xử lý tài khoản bị khóa.
- **Sản phẩm (Product Catalog)**: Hiển thị danh sách sản phẩm, tìm kiếm, lọc theo tiêu chí (Brand, CPU, RAM, Giá) và phân trang.
- **Giỏ hàng (Shopping Cart)**: Quản lý giỏ hàng (thêm, sửa số lượng, xóa) dựa trên HTTP Session, kiểm tra mức tồn kho (stock) hợp lệ.
- **Thanh toán & Đơn hàng (Checkout & Order)**: Đặt hàng, tính tổng tiền, thanh toán COD, trừ tồn kho an toàn bằng cơ chế Database Transaction (`FOR UPDATE` và Rollback).
- **Quản trị viên (Admin & Inventory)**: Quản lý trạng thái đơn hàng (pending -> delivered), xử lý hủy đơn (hoàn tồn kho), và quản lý nhập kho (`inventory_logs`).

---

## 🛠 Cài Đặt Môi Trường & Chạy Ứng Dụng

### 1. Yêu cầu hệ thống
- Python 3.10+
- Hệ điều hành: Windows / macOS / Linux

### 2. Cài đặt thư viện
Mở Terminal / Command Prompt tại thư mục dự án và chạy lệnh sau để cài đặt toàn bộ thư viện cần thiết cho việc chạy Web và Kiểm thử:
```bash
pip install -r requirements_test.txt
```

### 3. Khởi chạy Website (Manual Testing)
Nếu bạn muốn tự tay trải nghiệm các tính năng trên giao diện trình duyệt, hãy chạy ứng dụng bằng lệnh:
```bash
python app.py
```
Sau đó mở trình duyệt web và truy cập địa chỉ: `http://127.0.0.1:5000`

---

## 🧪 Hướng Dẫn Chạy Kiểm Thử Tự Động (Automation Testing)

Dự án sử dụng `pytest` làm testing framework. Toàn bộ kịch bản test nằm trong thư mục `tests/`. Cơ sở dữ liệu đã được giả lập hoàn toàn (Mocking), do đó bạn **không cần bật MySQL Server** vẫn có thể chạy test bình thường.

> **Lưu ý trên Windows:** Để tránh lỗi hiển thị font tiếng Việt trong Terminal, hãy luôn thêm cờ `-X utf8` vào sau chữ `python`.

### 1. Chạy TOÀN BỘ kịch bản kiểm thử (42 Test Cases)
Lệnh này sẽ chạy toàn bộ Unit, Integration và System test.
```bash
python -X utf8 -m pytest tests/ -v
```

### 2. Chạy riêng lẻ từng cấp độ kiểm thử
Nếu bạn muốn chạy tách biệt từng phần:

*   **Chạy Unit Test (20 TC):**
    ```bash
    python -X utf8 -m pytest tests/unit/ -v
    ```
*   **Chạy Integration Test (12 TC):**
    ```bash
    python -X utf8 -m pytest tests/integration/ -v
    ```
*   **Chạy System Test / E2E (10 TC):**
    ```bash
    python -X utf8 -m pytest tests/system/ -v
    ```

### 3. Chạy kiểm thử kèm đo lường độ bao phủ (Code Coverage)
Nếu muốn xuất báo cáo xem bộ test đã bao phủ bao nhiêu % mã nguồn:
```bash
python -X utf8 -m pytest tests/ -v --cov=. --cov-report=html
```
*(Báo cáo giao diện web sẽ được tạo trong thư mục `htmlcov/`. Mở file `htmlcov/index.html` bằng trình duyệt để xem).*

---

## 📊 Hệ Thống Tài Liệu Báo Cáo

Các tài liệu báo cáo kết quả kiểm thử đi kèm trong dự án này bao gồm:
1.  **Báo cáo bản Word:** `BAO CAO NHOM 6 (final).docx` (Chứa toàn bộ lý thuyết, kịch bản, và kết quả kiểm thử chi tiết).
2.  **Kịch bản Unit Test (Excel):** `Unit Test Case_fixed.xlsx`
3.  **Kịch bản Integration Test (Excel):** `IT_Test Case_fixed.xlsx`
4.  **Kịch bản System Test (Excel):** `ST_Test Case_fixed.xlsx`

**Kết quả đánh giá:** Cả 42/42 kịch bản đều được thực thi tự động thành công (Pass rate: 100%), chứng minh tính ổn định và tính toàn vẹn dữ liệu cao của hệ thống.
