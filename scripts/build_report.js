const {
  AlignmentType,
  BorderStyle,
  Document,
  Footer,
  Header,
  HeadingLevel,
  PageBreak,
  PageNumber,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  TableOfContents,
  WidthType,
} = require('docx');
const fs = require('fs');

const output = process.argv[2] || 'final_report.docx';
const navy = '1F4E78';
const blue = 'D9EAF7';
const light = 'F3F6F9';
const gray = '666666';

function text(value, options = {}) {
  return new TextRun({ text: String(value), font: 'Times New Roman', size: 24, ...options });
}

function para(value = '', options = {}) {
  const children = Array.isArray(value) ? value : [text(value)];
  return new Paragraph({
    children,
    alignment: options.alignment,
    spacing: { after: options.after ?? 120, line: 360 },
    indent: options.indent,
    heading: options.heading,
    pageBreakBefore: options.pageBreakBefore,
    keepNext: options.keepNext,
  });
}

function heading(value, level = HeadingLevel.HEADING_1) {
  return new Paragraph({
    text: value,
    heading: level,
    style: level,
    spacing: { before: 240, after: 120 },
  });
}

function bullet(value, level = 0) {
  return new Paragraph({
    children: [text(value)],
    bullet: { level },
    spacing: { after: 70, line: 300 },
  });
}

function numbered(value, level = 0) {
  return new Paragraph({
    children: [text(value)],
    numbering: { reference: 'report-numbering', level },
    spacing: { after: 70, line: 300 },
  });
}

function cell(value, options = {}) {
  const runs = Array.isArray(value) ? value : [text(value, { bold: options.bold ?? false, color: options.color })];
  return new TableCell({
    width: { size: options.width, type: WidthType.DXA },
    shading: options.shading ? { type: ShadingType.CLEAR, fill: options.shading } : undefined,
    verticalAlign: 'center',
    children: [new Paragraph({ children: runs, spacing: { after: 40, line: 260 } })],
  });
}

function table(headers, rows, widths) {
  const header = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => cell(h, { width: widths[i], bold: true, color: 'FFFFFF', shading: navy })),
  });
  const body = rows.map((row, rowIndex) => new TableRow({
    children: row.map((value, i) => cell(value, { width: widths[i], shading: rowIndex % 2 ? light : 'FFFFFF' })),
  }));
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: [header, ...body],
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: 'AAB7C4' },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: 'AAB7C4' },
      left: { style: BorderStyle.SINGLE, size: 4, color: 'AAB7C4' },
      right: { style: BorderStyle.SINGLE, size: 4, color: 'AAB7C4' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: 'D8E0E8' },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: 'D8E0E8' },
    },
  });
}

function codeBlock(lines) {
  return new Paragraph({
    children: [text(lines, { font: 'Consolas', size: 19, color: '333333' })],
    shading: { type: ShadingType.CLEAR, fill: 'F1F1F1' },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: navy } },
    indent: { left: 180, right: 180 },
    spacing: { before: 80, after: 140, line: 280 },
  });
}

const reqRows = [
  ['REQ-AUTH-01', 'Đăng ký tài khoản', 'Guest', 'Thông tin hợp lệ, email duy nhất, mật khẩu từ 6 ký tự', 'Tạo user và chuyển tới trang đăng nhập'],
  ['REQ-AUTH-02', 'Đăng nhập và phân quyền', 'Guest/User/Admin', 'Email, mật khẩu đúng; tài khoản không bị khóa', 'Tạo session; chuyển hướng theo role'],
  ['REQ-PROD-01', 'Xem và lọc sản phẩm', 'Guest/User', 'Chỉ hiển thị sản phẩm active; hỗ trợ keyword, brand, CPU, RAM, giá', 'Danh sách sản phẩm và tổng số kết quả'],
  ['REQ-CART-01', 'Quản lý giỏ hàng', 'Guest/User', 'Số lượng dương và không vượt stock', 'Session cart được cập nhật'],
  ['REQ-ORD-01', 'Đặt hàng', 'User', 'Đã đăng nhập, cart không rỗng, dữ liệu giao hàng hợp lệ', 'Tạo order, order details, trừ stock, xóa cart'],
  ['REQ-ORD-02', 'Kiểm soát tồn kho giao dịch', 'System/Database', 'Khóa dòng sản phẩm bằng FOR UPDATE', 'Rollback toàn bộ khi có lỗi'],
  ['REQ-ORD-03', 'Quản lý trạng thái đơn', 'Admin', 'Chỉ chuyển theo state machine', 'Cập nhật trạng thái; hủy đơn hoàn stock'],
  ['REQ-ADM-01', 'Quản trị sản phẩm và đơn hàng', 'Admin', 'Route admin yêu cầu role admin', 'CRUD, dashboard, export CSV'],
  ['REQ-INV-01', 'Nhập kho và nhật ký kho', 'Admin', 'Quantity nhập phải lớn hơn 0', 'Tăng stock và ghi inventory log'],
];

const screenRows = [
  ['/login', 'Đăng nhập', 'email, password', 'Session, flash, redirect', 'Bắt buộc nhập đủ trường'],
  ['/register', 'Đăng ký', 'fullname, email, phone, password', 'Tạo tài khoản', 'Email/password/phone hợp lệ'],
  ['/', 'Trang chủ', 'Không có', 'Brand, sản phẩm mới', 'Chỉ sản phẩm active và còn hàng ở latest'],
  ['/products', 'Danh sách sản phẩm', 'keyword, brand, cpu, ram, price, sort, page', 'Danh sách + phân trang', 'Giá là số; mỗi trang 9 sản phẩm'],
  ['/products/detail/<id>', 'Chi tiết sản phẩm', 'product_id', 'Thông tin sản phẩm', 'Không tồn tại/inactive trả 404'],
  ['/cart/', 'Giỏ hàng', 'Session cart', 'Các mặt hàng, tổng tiền', 'Quantity và price được tính lại khi hiển thị'],
  ['/cart/add', 'Thêm giỏ', 'product_id, quantity', 'Flash, session cart', 'Active và stock đủ'],
  ['/checkout/', 'Thanh toán', 'Receiver, payment, note', 'Tạo order hoặc báo lỗi', 'Login, cart không rỗng, transaction'],
  ['/orders/', 'Lịch sử đơn', 'Session user_id', 'Danh sách order của user', 'Không lộ đơn của user khác'],
  ['/admin/', 'Dashboard admin', 'Session admin', 'Thống kê, đơn gần đây, low stock', 'Chỉ admin'],
  ['/admin/orders', 'Quản lý đơn', 'status filter', 'Danh sách đơn', 'Chỉ admin'],
  ['/admin/inventory/import', 'Nhập kho', 'product, supplier, quantity, note', 'Tăng stock, log', 'Quantity > 0'],
];

const unitRows = [
  ['UT-UTIL-01', 'format_price', '1234567', '1.234.567 ₫', 'P0'],
  ['UT-UTIL-02', 'format_price', 'None / abc', '0 ₫', 'P0'],
  ['UT-UTIL-03', 'safe_int', 'abc, default=7', '7', 'P0'],
  ['UT-AUTH-01', 'login_required', 'Không có user_id', 'Redirect /login', 'P0'],
  ['UT-AUTH-02', 'admin_required', 'role=user', 'Redirect /', 'P0'],
  ['UT-CART-01', 'cart.add', 'quantity > stock', 'Không thêm, flash cảnh báo', 'P0'],
  ['UT-CART-02', 'cart.update', 'quantity=0', 'Xóa mặt hàng', 'P0'],
  ['UT-ORD-01', 'State machine', 'pending → processing', 'Cho phép', 'P0'],
  ['UT-ORD-02', 'State machine', 'delivered → pending', 'Từ chối', 'P0'],
  ['UT-INV-01', 'inventory import', 'quantity=10', 'Ghi log và tăng stock', 'P1'],
];

const useCaseRows = [
  ['UC-AUTH-01', 'Đăng ký tài khoản', 'Guest', 'Người dùng chọn chức năng Đăng ký', 'Tạo tài khoản người dùng mới', 'Form đăng ký được hiển thị; email chưa tồn tại', 'Bản ghi user được lưu, password được hash, chuyển tới /login', 'Normal Flow: nhập fullname, email, phone, password, xác nhận password; hệ thống kiểm tra và tạo user.', 'E1: Thiếu trường; E2: email sai/trùng; E3: password dưới 6 ký tự hoặc xác nhận không khớp.', 'High', 'BR1 email duy nhất; BR2 password tối thiểu 6 ký tự; BR3 password không lưu dạng rõ.'],
  ['UC-AUTH-02', 'Đăng nhập và phân quyền', 'Guest/User/Admin', 'Người dùng gửi email và password tại /login', 'Tài khoản tồn tại và không bị khóa', 'Tạo session user_id, role, email; redirect user về / hoặc admin về /admin', 'Normal Flow: nhập thông tin; tìm user; so sánh password hash; kiểm tra locked; tạo session và redirect theo role.', 'E1: Bỏ trống; E2: email không tồn tại/password sai; E3: tài khoản bị khóa.', 'High', 'BR1 chỉ tài khoản không khóa được đăng nhập; BR2 admin và user có redirect khác nhau.'],
  ['UC-PROD-01', 'Xem, tìm kiếm và lọc sản phẩm', 'Guest/User', 'Người dùng mở trang sản phẩm hoặc gửi bộ lọc', 'Có dữ liệu sản phẩm active', 'Hiển thị danh sách, chi tiết, sắp xếp và phân trang', 'Normal Flow: nhập keyword/brand/CPU/RAM/giá; hệ thống lọc sản phẩm active; hiển thị tối đa 9 sản phẩm/trang.', 'E1: product_id không tồn tại/inactive; E2: page hoặc giá không hợp lệ thì dùng giá trị mặc định an toàn.', 'High', 'BR1 chỉ hiển thị is_active=1; BR2 page bắt đầu từ 1; BR3 sort thuộc danh sách cho phép.'],
  ['UC-CART-01', 'Quản lý giỏ hàng', 'Guest/User', 'Người dùng thêm, sửa hoặc xóa sản phẩm', 'Sản phẩm active và còn tồn kho', 'Session cart được cập nhật và tổng tiền được tính lại', 'Normal Flow: chọn sản phẩm và quantity; kiểm tra stock; thêm/cập nhật session cart; hiển thị tổng tiền.', 'E1: sản phẩm không tồn tại/inactive; E2: quantity bằng 0 thì xóa; E3: quantity vượt stock thì báo lỗi.', 'High', 'BR1 quantity thêm vào phải dương; BR2 tổng quantity không vượt stock; BR3 cart lưu trong session.'],
  ['UC-ORD-01', 'Đặt hàng và thanh toán', 'User', 'Người dùng gửi form checkout', 'Đã đăng nhập, cart không rỗng, dữ liệu nhận hàng hợp lệ', 'Tạo order và order_details, trừ stock, xóa cart, redirect success', 'Normal Flow: nhập người nhận và payment; khóa stock bằng FOR UPDATE; kiểm tra tồn; tạo order/detail; commit transaction.', 'E1: chưa đăng nhập; E2: cart rỗng; E3: stock không đủ hoặc lỗi DB thì rollback và giữ cart.', 'High', 'BR1 transaction phải atomic; BR2 payment_method thuộc cod/bank_transfer/momo; BR3 stock không âm.'],
  ['UC-ORD-02', 'Quản lý trạng thái đơn hàng', 'Admin', 'Admin cập nhật trạng thái đơn', 'Admin đăng nhập và order tồn tại', 'Trạng thái chuyển theo state machine; hủy đơn hoàn stock', 'Normal Flow: mở danh sách/chi tiết; chọn trạng thái kế tiếp; hệ thống kiểm tra transition và cập nhật.', 'E1: transition không hợp lệ; E2: order delivered/cancelled không được chuyển tiếp; E3: hủy lỗi thì rollback.', 'High', 'BR1 pending → processing/cancelled; BR2 processing → shipping/cancelled; BR3 shipping → delivered.'],
  ['UC-ADM-01', 'Quản trị sản phẩm, user và đơn hàng', 'Admin', 'Admin mở khu vực quản trị', 'Session có role=admin', 'CRUD, dashboard, khóa user, cập nhật đơn và export CSV', 'Normal Flow: truy cập dashboard; chọn module; nhập dữ liệu; hệ thống kiểm tra quyền và lưu thay đổi.', 'E1: user thường truy cập; E2: dữ liệu/file không hợp lệ; E3: không cho admin tự khóa chính mình.', 'High', 'BR1 mọi route admin yêu cầu admin_required; BR2 file ảnh tối đa 1MB và đúng định dạng.'],
  ['UC-INV-01', 'Nhập kho và ghi nhật ký kho', 'Admin', 'Admin gửi form nhập kho', 'Sản phẩm, supplier tồn tại; quantity > 0', 'Stock tăng và inventory_logs được tạo', 'Normal Flow: chọn product/supplier; nhập quantity; tạo log; cập nhật stock; commit transaction.', 'E1: quantity không hợp lệ; E2: product/supplier không tồn tại; E3: lỗi DB thì rollback.', 'Medium', 'BR1 import tăng stock; BR2 log phải lưu type và quantity; BR3 thao tác dùng transaction.'],
];

const unitDetailRows = [
  ['UT-UTIL-01', 'Định dạng giá tiền số nguyên', 'Không yêu cầu DB', 'value=1234567', 'Gọi format_price(value)', 'Hiển thị 1.234.567 ₫', 'High'],
  ['UT-UTIL-02', 'Xử lý giá trị rỗng/sai kiểu', 'Không yêu cầu DB', 'value=None hoặc abc', 'Gọi format_price(value)', 'Trả về 0 ₫, không phát sinh exception', 'High'],
  ['UT-AUTH-01', 'Chặn user chưa đăng nhập', 'Không có user_id trong session', 'Request /private', 'Gọi hàm được trang trí login_required', 'Redirect tới /login', 'High'],
  ['UT-AUTH-02', 'Chặn user thường vào admin', 'Session role=user', 'Request /admin/private', 'Gọi hàm được trang trí admin_required', 'Redirect về /', 'High'],
  ['UT-CART-01', 'Từ chối quantity vượt stock', 'Product active, stock=5', 'product_id=1, quantity=10', 'Mock ProductModel; POST /cart/add', 'Không thêm item và hiển thị cảnh báo', 'High'],
  ['UT-ORD-01', 'Cho phép chuyển trạng thái hợp lệ', 'Order status=pending', 'new_status=processing', 'Gọi update_status()', 'Cập nhật thành công', 'High'],
  ['UT-ORD-02', 'Từ chối chuyển trạng thái sai', 'Order status=delivered', 'new_status=pending', 'Gọi update_status()', 'Từ chối transition', 'High'],
];

const integrationDetailRows = [
  ['IT-AUTH-01', 'Tạo user qua controller và DB', 'Database test sạch', 'fullname/email/password hợp lệ', 'POST /register; truy vấn users', 'User được tạo, password đã hash', 'High'],
  ['IT-AUTH-02', 'Đăng nhập và tạo session', 'User tồn tại, is_locked=0', 'Email/password đúng', 'POST /login; kiểm tra session', 'Session chứa id/role và redirect đúng', 'High'],
  ['IT-PROD-01', 'Lọc sản phẩm với DB', 'Có product active/inactive', 'brand=ASUS', 'GET /products?brand=ASUS; kiểm tra kết quả', 'Chỉ trả product active đúng brand', 'High'],
  ['IT-ORD-01', 'Tạo order và trừ stock', 'User login, cart đủ stock', 'Cart quantity=2', 'POST /checkout; truy vấn order/detail/product', 'Order/detail tạo, stock giảm, cart xóa', 'High'],
  ['IT-ORD-02', 'Rollback khi tạo order lỗi', 'DB test sẵn sàng', 'Giả lập lỗi insert detail', 'POST /checkout; kiểm tra DB sau lỗi', 'Không còn order dang dở, stock không đổi', 'High'],
  ['IT-ORD-03', 'Hủy order và hoàn stock', 'Order pending có detail', 'status=cancelled', 'Admin cập nhật status; truy vấn DB', 'Order cancelled, stock hoàn đúng quantity', 'High'],
];

const systemDetailRows = [
  ['ST-01', 'Mua hàng thành công', 'Guest/User; product còn stock', 'Product id=1, quantity=2, COD', 'Đăng nhập → xem product → add cart → checkout → submit', 'Order pending; stock giảm; cart được xóa', 'High'],
  ['ST-02', 'Checkout khi hết hàng', 'User login; cart có item', 'Quantity trong cart lớn hơn stock hiện tại', 'Mở checkout và submit form', 'Hiển thị lỗi; không tạo order; cart giữ nguyên', 'High'],
  ['ST-03', 'Admin xử lý đơn', 'Order pending; admin login', 'order_id hợp lệ', 'Cập nhật pending → processing → shipping → delivered', 'Mỗi transition hợp lệ và trạng thái cuối delivered', 'High'],
  ['ST-04', 'User truy cập vùng admin', 'User thường đã login', 'GET /admin/', 'Gửi request trực tiếp tới route admin', 'Redirect về /, không thực hiện thao tác admin', 'High'],
  ['ST-05', 'Admin nhập kho', 'Admin login; product/supplier tồn tại', 'quantity=10, type=import', 'Mở form → nhập dữ liệu → submit', 'Stock tăng 10 và có inventory log', 'Medium'],
];

const integrationRows = [
  ['IT-AUTH-01', 'Auth + Users DB', 'Đăng ký email mới', 'Row users được tạo, password đã hash', 'REQ-AUTH-01'],
  ['IT-AUTH-02', 'Auth + Users DB', 'Đăng nhập user hợp lệ', 'Session chứa id/role', 'REQ-AUTH-02'],
  ['IT-PROD-01', 'Products + DB', 'Lọc brand ASUS', 'SQL parameterized trả đúng sản phẩm active', 'REQ-PROD-01'],
  ['IT-CART-01', 'Cart + Session', 'Thêm sản phẩm số lượng 2', 'Session cart có item đúng quantity', 'REQ-CART-01'],
  ['IT-ORD-01', 'Checkout + Order DB', 'Tạo order đủ stock', 'Order/detail tạo và stock giảm', 'REQ-ORD-01'],
  ['IT-ORD-02', 'Order transaction', 'Lỗi insert detail', 'Rollback order và stock', 'REQ-ORD-02'],
  ['IT-ORD-03', 'Order state + Inventory', 'Hủy đơn pending', 'Status cancelled và hoàn stock', 'REQ-ORD-03'],
  ['IT-ADM-01', 'Admin + CSV', 'Export orders', 'CSV có BOM và header đúng', 'REQ-ADM-01'],
  ['IT-INV-01', 'Inventory + DB', 'Nhập kho quantity=10', 'Log import và stock +10', 'REQ-INV-01'],
];

const systemRows = [
  ['ST-01', 'User mua hàng thành công', 'Guest/User, sản phẩm còn stock', 'Order pending; stock giảm; cart xóa', 'P0'],
  ['ST-02', 'Checkout khi hết hàng', 'Cart có quantity vượt stock hiện tại', 'Báo lỗi; không tạo order; cart giữ nguyên', 'P0'],
  ['ST-03', 'Admin xử lý đơn', 'Order pending, admin đăng nhập', 'pending → processing → shipping → delivered', 'P0'],
  ['ST-04', 'Admin hủy đơn', 'Order pending và order detail tồn tại', 'cancelled; stock hoàn đúng một lần', 'P1'],
  ['ST-05', 'Admin nhập kho', 'Admin, product, quantity dương', 'Stock tăng và inventory log xuất hiện', 'P1'],
  ['ST-06', 'User truy cập vùng admin', 'User thường đã đăng nhập', 'Redirect trang chủ, không thực hiện thao tác', 'P0'],
  ['ST-07', 'Xem đơn của user khác', 'Có order_id không thuộc user', 'Không hiển thị chi tiết đơn', 'P0'],
];

const bugRows = [
  ['BUG-CAND-01', 'Price filter nhận dữ liệu không phải số gây ValueError', 'Nhập price_min=abc tại /products', 'Hiển thị kết quả hoặc thông báo hợp lệ', 'Có thể phát sinh lỗi 500', 'High', 'Chưa xác nhận'],
  ['BUG-CAND-02', 'Cart update dereference product null', 'Thêm item rồi xóa product, POST /cart/update', 'Báo sản phẩm không tồn tại', 'Có thể lỗi TypeError', 'High', 'Chưa xác nhận'],
  ['BUG-CAND-03', 'Quantity âm khi thêm giỏ', 'POST quantity=-1', 'Từ chối quantity không hợp lệ', 'Có thể tạo cart với quantity âm', 'High', 'Chưa xác nhận'],
  ['BUG-CAND-04', 'Export inventory có thể làm stock âm', 'Xuất quantity lớn hơn stock', 'Từ chối và giữ stock không âm', 'Có thể stock âm', 'High', 'Chưa xác nhận'],
  ['BUG-CAND-05', 'Regex phone cho phép ký tự |', 'Đăng ký số bắt đầu bằng |', 'Từ chối số điện thoại sai', 'Có thể chấp nhận ngoài ý muốn', 'Medium', 'Chưa xác nhận'],
  ['BUG-CAND-06', 'Mutation dùng GET thiếu bảo vệ CSRF', 'Gửi GET toggle/delete từ nguồn ngoài', 'Chỉ mutation qua POST có CSRF', 'Có nguy cơ thay đổi ngoài ý muốn', 'High', 'Chưa xác nhận'],
];

const traceRows = [
  ['REQ-AUTH-01', 'UT-AUTH-03, IT-AUTH-01, ST-08', 'Đăng ký tài khoản'],
  ['REQ-AUTH-02', 'UT-AUTH-01, IT-AUTH-02, ST-06', 'Đăng nhập và phân quyền'],
  ['REQ-PROD-01', 'UT-PROD-01..12, IT-PROD-01, ST-09', 'Catalog/filter'],
  ['REQ-CART-01', 'UT-CART-01..10, IT-CART-01, ST-01', 'Shopping cart'],
  ['REQ-ORD-01', 'UT-ORD-03..15, IT-ORD-01..02, ST-01..02', 'Checkout'],
  ['REQ-ORD-03', 'UT-ORD-16..30, IT-ORD-03, ST-03..04', 'State machine'],
  ['REQ-ADM-01', 'UT-ADM-01..18, IT-ADM-01, ST-03', 'Admin'],
  ['REQ-INV-01', 'UT-INV-01..10, IT-INV-01, ST-05', 'Inventory'],
];

const children = [];
children.push(
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 600, after: 120 },
    children: [text('TRƯỜNG ĐẠI HỌC ………………………', { bold: true, size: 28, color: navy })],
  }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [text('KHOA CÔNG NGHỆ THÔNG TIN', { bold: true, size: 28, color: navy })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 400 }, children: [text('BÁO CÁO BÀI TẬP LỚN', { bold: true, size: 34, color: navy })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 180 }, children: [text('MÔN: KIỂM THỬ PHẦN MỀM', { bold: true, size: 30 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 240 }, children: [text('ĐỀ TÀI', { bold: true, size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 800 }, children: [text('XÂY DỰNG KẾ HOẠCH VÀ THỰC HIỆN KIỂM THỬ\nWEBSITE BÁN LAPTOP', { bold: true, size: 32, color: navy })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 800, after: 120 }, children: [text('Nhóm thực hiện: …………………………………', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [text('Giảng viên hướng dẫn: ………………………', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 900, after: 120 }, children: [text('Năm 2026', { size: 24 })] }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(heading('MỤC LỤC', HeadingLevel.TITLE));
children.push(new TableOfContents('Mục lục', { hyperlink: true, headingStyleRange: '1-3' }));
children.push(new Paragraph({ children: [new PageBreak()] }));

children.push(heading('LỜI MỞ ĐẦU', HeadingLevel.HEADING_1));
children.push(para('Trong quá trình phát triển phần mềm, kiểm thử giúp xác định mức độ phù hợp giữa sản phẩm triển khai và các yêu cầu nghiệp vụ, đồng thời phát hiện sớm các lỗi có thể ảnh hưởng đến dữ liệu, trải nghiệm người dùng và tính ổn định của hệ thống. Báo cáo này trình bày hoạt động kiểm thử đối với website bán laptop được xây dựng bằng Flask, Python và MySQL.'));
children.push(para('Đối tượng kiểm thử gồm các chức năng dành cho khách, người dùng đã đăng nhập và quản trị viên: xác thực tài khoản, tra cứu sản phẩm, giỏ hàng, đặt hàng, quản lý trạng thái đơn, quản lý sản phẩm, người dùng, nhà cung cấp và tồn kho. Báo cáo kết hợp unit test, integration test, system test và automation test để tạo quy trình kiểm thử có thể lặp lại.'));
children.push(para('Do bộ kiểm thử và môi trường MySQL được chuẩn bị trong phạm vi dự án nhưng chưa có kết quả chạy đầy đủ tại thời điểm lập tài liệu, các mục “kết quả thực thi” trong báo cáo được phân biệt rõ giữa kết quả đã xác định từ mã nguồn, kết quả dự kiến và các lỗi tiềm ẩn chưa được xác nhận.'));

children.push(heading('CHƯƠNG 1. TỔNG QUAN BÀI TOÁN', HeadingLevel.HEADING_1));
children.push(heading('1.1. Giới thiệu đề tài', HeadingLevel.HEADING_2));
children.push(para('Website LaptopStore là hệ thống bán laptop trực tuyến. Ứng dụng cung cấp danh mục sản phẩm, tìm kiếm/lọc, giỏ hàng, checkout, theo dõi đơn hàng và khu vực quản trị. Kiến trúc hiện tại sử dụng Flask application factory, Blueprint, Jinja template và các model truy cập MySQL thông qua PyMySQL.'));
children.push(heading('1.2. Đặc tả yêu cầu', HeadingLevel.HEADING_2));
children.push(heading('1.2.1. Các luồng nghiệp vụ chính', HeadingLevel.HEADING_3));
children.push(para('Các luồng nghiệp vụ chính của hệ thống được mô tả theo hướng end-to-end (E2E), từ thao tác của tác nhân đến kết quả cuối cùng và trạng thái dữ liệu.'));
children.push(para([text('Luồng E2E-01: Người dùng mua hàng thành công', { bold: true })]));
['Khách truy cập trang chủ hoặc danh sách sản phẩm.', 'Lọc/sắp xếp, mở chi tiết và thêm sản phẩm vào giỏ.', 'Cập nhật số lượng, đăng nhập hoặc đăng ký.', 'Nhập thông tin nhận hàng và phương thức thanh toán.', 'Hệ thống kiểm tra stock, tạo order và order_details trong transaction.', 'Trừ stock, xóa cart, chuyển tới trang thành công và cho phép xem lịch sử đơn.'].forEach((x) => children.push(numbered(x)));
children.push(para([text('Luồng E2E-03: Quản trị xử lý đơn hàng', { bold: true })]));
['Admin đăng nhập và mở dashboard.', 'Xem danh sách đơn, lọc theo trạng thái pending và mở chi tiết.', 'Chuyển pending → processing → shipping → delivered theo state machine.', 'Có thể hủy đơn ở trạng thái pending hoặc processing.', 'Khi hủy, hệ thống hoàn stock theo order_details; không cho phép chuyển tiếp từ delivered hoặc cancelled.'].forEach((x) => children.push(numbered(x)));
children.push(para([text('Luồng E2E-05: Quản trị nhập kho', { bold: true })]));
['Admin chọn sản phẩm, nhà cung cấp và quantity > 0.', 'Hệ thống tạo inventory_logs với type=import.', 'Cập nhật products.stock = stock + quantity và commit transaction.'].forEach((x) => children.push(numbered(x)));

children.push(heading('1.2.2. Các màn hình chức năng chính', HeadingLevel.HEADING_3));
children.push(para('Các màn hình chức năng được đặc tả dưới dạng Use Case theo chuẩn IEEE 830 và định dạng báo cáo kiểm thử chuyên nghiệp. Mỗi Use Case mô tả một chức năng chính của hệ thống với đầy đủ các trường: UC ID, tên chức năng, tác nhân chính, trigger, mô tả, tiền điều kiện, hậu điều kiện, luồng chính, ngoại lệ, độ ưu tiên và business rules.'));

// UC-AUTH-01: Đăng ký tài khoản
children.push(para([text('Use Case UC-AUTH-01: Đăng ký tài khoản', { bold: true, size: 24 })]));
children.push(table(['Trường', 'Giá trị'], [
  ['UC ID', 'UC-AUTH-01'],
  ['Tên UC', 'Đăng ký tài khoản'],
  ['Tác nhân chính', 'Guest'],
  ['Tác nhân phụ', 'Không'],
  ['Trigger', 'Người dùng chọn chức năng Đăng ký'],
  ['Mô tả', 'Tạo tài khoản người dùng mới với email, password và thông tin cá nhân'],
  ['Tiền điều kiện', 'PRE-1: Form đăng ký được hiển thị\nPRE-2: Email chưa tồn tại trong hệ thống'],
  ['Hậu điều kiện', 'POST-1: Bản ghi user được lưu, password được hash\nPOST-2: Chuyển tới trang /login'],
  ['Luồng chính', '1. Người dùng nhập fullname, email, phone, password, password_confirm\n2. Hệ thống kiểm tra tính hợp lệ\n3. Hệ thống hash password\n4. Hệ thống tạo user với role=user\n5. Hiển thị thông báo và chuyển tới /login'],
  ['Ngoại lệ', 'E1: Thiếu trường bắt buộc - thông báo lỗi\nE2: Email sai định dạng hoặc đã tồn tại - thông báo lỗi\nE3: Password dưới 6 ký tự hoặc xác nhận không khớp - thông báo lỗi'],
  ['Độ ưu tiên', 'High'],
  ['Business Rules', 'BR1: Email phải duy nhất trong hệ thống\nBR2: Password tối thiểu 6 ký tự\nBR3: Password không được lưu dạng rõ, phải hash bằng Werkzeug'],
], [2500, 6960]));

// UC-AUTH-02: Đăng nhập
children.push(para([text('Use Case UC-AUTH-02: Đăng nhập và phân quyền', { bold: true, size: 24 })]));
children.push(table(['Trường', 'Giá trị'], [
  ['UC ID', 'UC-AUTH-02'],
  ['Tên UC', 'Đăng nhập và phân quyền'],
  ['Tác nhân chính', 'Guest/User/Admin'],
  ['Tác nhân phụ', 'Không'],
  ['Trigger', 'Người dùng gửi email và password tại /login'],
  ['Mô tả', 'Xác thực tài khoản và tạo session theo role'],
  ['Tiền điều kiện', 'PRE-1: Tài khoản tồn tại và không bị khóa (is_locked=0)'],
  ['Hậu điều kiện', 'POST-1: Session chứa user_id, role, email\nPOST-2: Redirect user về / hoặc admin về /admin'],
  ['Luồng chính', '1. Người dùng nhập email và password\n2. Hệ thống tìm user theo email\n3. Hệ thống so sánh password với password hash\n4. Hệ thống kiểm tra is_locked\n5. Tạo session và redirect theo role'],
  ['Ngoại lệ', 'E1: Bỏ trống email hoặc password\nE2: Email không tồn tại hoặc password sai\nE3: Tài khoản bị khóa (is_locked=1)'],
  ['Độ ưu tiên', 'High'],
  ['Business Rules', 'BR1: Chỉ tài khoản không khóa được đăng nhập\nBR2: Admin redirect /admin, user redirect /'],
], [2500, 6960]));

// UC-PROD-01: Xem sản phẩm
children.push(para([text('Use Case UC-PROD-01: Xem, tìm kiếm và lọc sản phẩm', { bold: true, size: 24 })]));
children.push(table(['Trường', 'Giá trị'], [
  ['UC ID', 'UC-PROD-01'],
  ['Tên UC', 'Xem, tìm kiếm và lọc sản phẩm'],
  ['Tác nhân chính', 'Guest/User'],
  ['Tác nhân phụ', 'Không'],
  ['Trigger', 'Người dùng mở trang sản phẩm hoặc gửi bộ lọc'],
  ['Mô tả', 'Hiển thị danh sách sản phẩm với tìm kiếm, lọc, sắp xếp và phân trang'],
  ['Tiền điều kiện', 'PRE-1: Có dữ liệu sản phẩm active trong database'],
  ['Hậu điều kiện', 'POST-1: Danh sách sản phẩm được hiển thị theo bộ lọc\nPOST-2: Phân trang hoạt động đúng'],
  ['Luồng chính', '1. Người dùng nhập keyword, chọn brand/CPU/RAM/giá, chọn sắp xếp\n2. Hệ thống lọc sản phẩm active (is_active=1)\n3. Hiển thị tối đa 9 sản phẩm/trang với phân trang'],
  ['Ngoại lệ', 'E1: product_id không tồn tại hoặc inactive - trả 404\nE2: page hoặc giá không hợp lệ - dùng giá trị mặc định'],
  ['Độ ưu tiên', 'High'],
  ['Business Rules', 'BR1: Chỉ hiển thị sản phẩm is_active=1\nBR2: page bắt đầu từ 1\nBR3: sort thuộc danh sách cho phép'],
], [2500, 6960]));

// UC-CART-01: Giỏ hàng
children.push(para([text('Use Case UC-CART-01: Quản lý giỏ hàng', { bold: true, size: 24 })]));
children.push(table(['Trường', 'Giá trị'], [
  ['UC ID', 'UC-CART-01'],
  ['Tên UC', 'Quản lý giỏ hàng'],
  ['Tác nhân chính', 'Guest/User'],
  ['Tác nhân phụ', 'Không'],
  ['Trigger', 'Người dùng thêm, sửa hoặc xóa sản phẩm trong giỏ'],
  ['Mô tả', 'Thêm/cập nhật/xóa sản phẩm trong session cart'],
  ['Tiền điều kiện', 'PRE-1: Sản phẩm active và còn tồn kho'],
  ['Hậu điều kiện', 'POST-1: Session cart được cập nhật\nPOST-2: Tổng tiền được tính lại'],
  ['Luồng chính', '1. Người dùng chọn sản phẩm và quantity\n2. Hệ thống kiểm tra stock\n3. Thêm hoặc cập nhật session cart\n4. Hiển thị tổng tiền'],
  ['Ngoại lệ', 'E1: Sản phẩm không tồn tại hoặc inactive\nE2: quantity=0 thì xóa item\nE3: quantity vượt stock thì báo lỗi'],
  ['Độ ưu tiên', 'High'],
  ['Business Rules', 'BR1: quantity phải dương\nBR2: Tổng quantity không vượt stock\nBR3: Cart lưu trong session'],
], [2500, 6960]));

// UC-ORD-01: Đặt hàng
children.push(para([text('Use Case UC-ORD-01: Đặt hàng và thanh toán', { bold: true, size: 24 })]));
children.push(table(['Trường', 'Giá trị'], [
  ['UC ID', 'UC-ORD-01'],
  ['Tên UC', 'Đặt hàng và thanh toán'],
  ['Tác nhân chính', 'User'],
  ['Tác nhân phụ', 'Không'],
  ['Trigger', 'Người dùng gửi form checkout'],
  ['Mô tả', 'Tạo order và order_details, trừ stock, xóa cart'],
  ['Tiền điều kiện', 'PRE-1: Đã đăng nhập\nPRE-2: Cart không rỗng\nPRE-3: Dữ liệu nhận hàng hợp lệ'],
  ['Hậu điều kiện', 'POST-1: Order và order_details được tạo\nPOST-2: Stock giảm đúng quantity\nPOST-3: Cart được xóa\nPOST-4: Redirect success'],
  ['Luồng chính', '1. Người dùng nhập thông tin người nhận và chọn payment\n2. Hệ thống khóa stock bằng FOR UPDATE\n3. Kiểm tra tồn kho\n4. Tạo order và order_details\n5. Commit transaction\n6. Xóa cart và redirect'],
  ['Ngoại lệ', 'E1: Chưa đăng nhập - redirect /login\nE2: Cart rỗng - redirect và báo lỗi\nE3: Stock không đủ hoặc lỗi DB - rollback và giữ cart'],
  ['Độ ưu tiên', 'High'],
  ['Business Rules', 'BR1: Transaction phải atomic\nBR2: payment_method thuộc cod/bank_transfer/momo\nBR3: Stock không được âm'],
], [2500, 6960]));

children.push(para([text('Chi tiết màn hình và trường dữ liệu', { bold: true })]));
children.push(para([text('Màn hình đăng nhập (/login)', { bold: true })]));
children.push(para('Wireframe: Form căn giữa gồm email, password, nút Đăng nhập, link Đăng ký và khu vực hiển thị flash message. Template có thêm thông tin tài khoản demo để hỗ trợ kiểm tra thủ công.'));
children.push(table(['Trường', 'Kiểu dữ liệu', 'Độ dài/Format', 'Bắt buộc', 'Ràng buộc'], [
  ['email', 'string', 'Email hợp lệ', 'Có', 'Email phải tồn tại; so sánh password với password hash'],
  ['password', 'string', 'Tối thiểu 6 ký tự', 'Có', 'Tài khoản is_locked=1 không được đăng nhập'],
], [1800, 1600, 2100, 1200, 3660]));
children.push(para([text('Màn hình đăng ký (/register)', { bold: true })]));
children.push(para('Wireframe: Form dọc gồm fullname, email, phone, password, password_confirm; bên dưới là nút Đăng ký và link quay lại đăng nhập.'));
children.push(table(['Trường', 'Kiểu dữ liệu', 'Độ dài/Format', 'Bắt buộc', 'Ràng buộc'], [
  ['fullname', 'string', 'Tối đa 100 ký tự', 'Có', 'Không rỗng'],
  ['email', 'string', 'Email hợp lệ', 'Có', 'Regex email và duy nhất trong database'],
  ['phone', 'string', '10-11 chữ số', 'Không', 'Kiểm tra regex nếu người dùng nhập'],
  ['password', 'string', 'Tối thiểu 6 ký tự', 'Có', 'Hash trước khi lưu'],
  ['password_confirm', 'string', 'Tối thiểu 6 ký tự', 'Có', 'Phải khớp password'],
], [1800, 1600, 2100, 1200, 3660]));
children.push(para([text('Màn hình danh sách sản phẩm (/products)', { bold: true })]));
children.push(para('Wireframe: Thanh tìm kiếm, nhóm bộ lọc brand/CPU/RAM/giá, lựa chọn sắp xếp, lưới sản phẩm và phân trang. Mỗi thẻ sản phẩm hiển thị ảnh, tên, giá và thao tác thêm vào giỏ.'));
children.push(table(['Trường', 'Kiểu dữ liệu', 'Độ dài/Format', 'Bắt buộc', 'Ràng buộc'], [
  ['keyword', 'string', 'Tối đa 100 ký tự', 'Không', 'Tìm kiếm theo tên/mô tả sản phẩm'],
  ['brand', 'enum/string', 'Giá trị từ danh sách brand', 'Không', 'Lọc theo brand hoặc bỏ qua khi rỗng'],
  ['cpu', 'enum/string', 'Giá trị preset', 'Không', 'Lọc theo CPU'],
  ['ram', 'enum', '8GB/16GB/32GB', 'Không', 'Lọc theo RAM'],
  ['price_min', 'integer', 'Số nguyên >= 0', 'Không', 'Giá trị phải là số hợp lệ'],
  ['price_max', 'integer', 'Số nguyên >= 0', 'Không', 'Giá trị phải là số hợp lệ và >= price_min'],
  ['sort', 'enum', 'newest/price_asc/price_desc/name_asc', 'Không', 'Mặc định newest'],
  ['page', 'integer', '>= 1', 'Không', 'Mặc định 1; mỗi trang 9 sản phẩm'],
], [1400, 1500, 2100, 1100, 4260]));
children.push(para([text('Màn hình thanh toán (/checkout)', { bold: true })]));
children.push(para('Wireframe: Cột trái là form thông tin người nhận và phương thức thanh toán; cột phải là tóm tắt các sản phẩm, số lượng, đơn giá và tổng tiền; cuối form có nút Đặt hàng.'));
children.push(table(['Trường', 'Kiểu dữ liệu', 'Độ dài/Format', 'Bắt buộc', 'Ràng buộc'], [
  ['receiver_name', 'string', 'Tối đa 100 ký tự', 'Có', 'Không rỗng'],
  ['receiver_phone', 'string', '10-11 chữ số', 'Có', 'Kiểm tra định dạng số điện thoại'],
  ['receiver_address', 'text', 'Tối đa 500 ký tự', 'Có', 'Không rỗng'],
  ['payment_method', 'enum', 'cod/bank_transfer/momo', 'Có', 'Chỉ chấp nhận giá trị trong danh sách'],
  ['note', 'text', 'Tối đa 500 ký tự', 'Không', 'Ghi chú giao hàng'],
], [1800, 1600, 2100, 1200, 3660]));
children.push(table(['Route', 'Màn hình', 'Input', 'Output', 'Ràng buộc'], screenRows, [1900, 1750, 2800, 2200, 1210]));

children.push(heading('1.2.3. Các Module chính của chương trình', HeadingLevel.HEADING_3));
children.push(table(['Module', 'Input', 'Output', 'Mô tả chức năng'], [
  ['Authentication', 'email, password, fullname, phone, password_confirm', 'Session user, flash, redirect', 'Đăng ký, hash password, đăng nhập, kiểm tra tài khoản bị khóa, phân quyền user/admin và đăng xuất.'],
  ['Product Catalog', 'keyword, brand, cpu, ram, price_min, price_max, sort, page, product_id', 'Danh sách active, chi tiết, brands, pagination', 'Tìm kiếm, lọc, sắp xếp, phân trang và hiển thị chi tiết sản phẩm.'],
  ['Shopping Cart', 'product_id, quantity', 'Session cart, tổng tiền, flash, redirect', 'Thêm, cập nhật, xóa item và kiểm tra quantity không vượt stock.'],
  ['Checkout & Order', 'user_id, thông tin nhận hàng, payment_method, note, cart', 'order_id, order_details, stock cập nhật, redirect success', 'Kiểm tra login/cart, khóa dòng bằng FOR UPDATE, tạo order trong transaction, rollback khi lỗi và xóa cart khi thành công.'],
  ['Order Management', 'user_id, order_id, status', 'Danh sách/chi tiết order, status mới, hoàn stock', 'User xem đơn của mình; admin cập nhật state machine và hủy đơn hoàn stock.'],
  ['Admin CRUD', 'product data, order_id, user_id, status, file upload', 'CRUD, dashboard, CSV export', 'Quản lý sản phẩm, đơn, user, upload ảnh, thống kê và export CSV UTF-8 BOM.'],
  ['Inventory', 'product_id, supplier_id, quantity, type, note', 'inventory_logs, stock cập nhật', 'Nhập kho, xuất kho và điều chỉnh tồn kho; ghi log và xử lý transaction.'],
], [1600, 2500, 2200, 3160]));

children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading('CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ TEST', HeadingLevel.HEADING_1));
children.push(heading('2.1. Unit test case', HeadingLevel.HEADING_2));
children.push(heading('2.1.1. Phương pháp, kỹ thuật', HeadingLevel.HEADING_3));
children.push(para('Unit test cô lập một hàm, helper hoặc route logic để kiểm tra hành vi độc lập mà không phụ thuộc database hoặc component khác. Các hàm thuần trong helpers được kiểm thử trực tiếp bằng assertion; route test sử dụng Flask test client và mock model tại namespace controller để tránh kết nối MySQL thật.'));
children.push(para('Kỹ thuật chính: Equivalence Partitioning (phân vùng input hợp lệ/không hợp lệ), Boundary Value Analysis (giá trị biên như password 5/6/7 ký tự, quantity 0/1/stock/stock+1), và Decision Table cho logic phân quyền. Công cụ sử dụng pytest, unittest.mock.patch và Flask app.test_client(). Mock patch phải trỏ đúng namespace nơi symbol được import (ví dụ controllers.auth.UserModel thay vì models.user.UserModel).'));
children.push(heading('2.1.2. Danh sách test case', HeadingLevel.HEADING_3));
children.push(para('Định dạng danh sách test case được xây dựng theo mẫu UC1: Add New Product, gồm mã test case, mục tiêu kiểm thử, tiền điều kiện, dữ liệu kiểm thử, các bước thực hiện, kết quả mong đợi và mức ưu tiên. Kết quả dưới đây là kết quả mong đợi; trạng thái Pass/Fail chỉ được ghi sau khi thực thi thực tế.'));
children.push(table(['TC ID', 'Mục tiêu kiểm thử', 'Tiền điều kiện', 'Dữ liệu kiểm thử', 'Các bước thực hiện', 'Kết quả mong đợi', 'Priority'], unitDetailRows, [1000, 1700, 1600, 1500, 1900, 2100, 660]));

children.push(heading('2.2. Integration test case', HeadingLevel.HEADING_2));
children.push(heading('2.2.1. Phương pháp, kỹ thuật', HeadingLevel.HEADING_3));
children.push(para('Integration test kiểm tra sự kết hợp giữa controller, model, Flask session và database test. Database test phải tách khỏi database phát triển; seed dữ liệu trước mỗi test và cleanup sau test để tránh phụ thuộc thứ tự. Các test case tập trung vào SQL parameterized, transaction commit/rollback và đảm bảo state database đúng sau mỗi thao tác.'));
children.push(para('Kỹ thuật chính: kiểm tra integration path giữa route và model; Decision Table cho luồng có nhiều điều kiện rẽ nhánh (ví dụ đăng nhập kiểm tra user tồn tại/password đúng/locked/role); State Transition cho order state machine. Test phải verify cả output trả về và dữ liệu lưu trong database (SELECT sau INSERT/UPDATE). Công cụ pytest với fixture database và Flask test client.'));
children.push(heading('2.2.2. Danh sách test case', HeadingLevel.HEADING_3));
children.push(table(['TC ID', 'Mục tiêu kiểm thử', 'Tiền điều kiện', 'Dữ liệu kiểm thử', 'Các bước thực hiện', 'Kết quả mong đợi', 'Priority'], integrationDetailRows, [1000, 1700, 1600, 1500, 1900, 2100, 660]));

children.push(heading('2.3. System test case', HeadingLevel.HEADING_2));
children.push(heading('2.3.1. Phương pháp, kỹ thuật', HeadingLevel.HEADING_3));
children.push(para('System test mô phỏng hành vi người dùng từ đầu đến cuối (end-to-end), bao gồm nhiều route và module. Flask test client được dùng cho route-level flow; Selenium được chuẩn bị cho browser automation khi cần kiểm tra JavaScript behavior, responsive layout hoặc tích hợp với service bên ngoài.'));
children.push(para('Kỹ thuật chính: Cause-Effect Graph (checkout yêu cầu logged in AND cart not empty AND stock sufficient), State Transition (order status machine với 18 test case bao gồm cả hợp lệ và không hợp lệ), và kiểm tra integration giữa nhiều module (auth → cart → checkout → order → inventory). Test phải verify kết quả cuối: order được tạo, stock giảm đúng, cart xóa và redirect đúng trang. Mỗi flow yêu cầu assertion về state database, session và response code.'));
children.push(heading('2.3.2. Danh sách test case', HeadingLevel.HEADING_3));
children.push(table(['TC ID', 'Mục tiêu kiểm thử', 'Tiền điều kiện', 'Dữ liệu kiểm thử', 'Các bước thực hiện', 'Kết quả mong đợi', 'Priority'], systemDetailRows, [1000, 1700, 1600, 1500, 1900, 2100, 660]));

children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading('CHƯƠNG 3. THỰC THI TEST VÀ BÁO CÁO KẾT QUẢ', HeadingLevel.HEADING_1));
children.push(heading('3.1. Môi trường và trạng thái thực thi', HeadingLevel.HEADING_2));
children.push(table(['Hạng mục', 'Giá trị'], [
  ['Ứng dụng', 'Flask 3.0.0, Python, server local port 5000'],
  ['Database', 'MySQL/XAMPP, schema laptop_store.sql và phần mở rộng upgrade_v2.sql'],
  ['Unit/integration framework', 'pytest, Flask test client, unittest.mock, pytest-cov'],
  ['Browser automation', 'Selenium được chuẩn bị cho các flow đại diện; chưa có kết quả browser run trong phiên lập báo cáo'],
  ['Trạng thái hiện tại', 'Đã tạo requirements_test.txt, fixture Flask và một số unit/route test; chưa chạy đầy đủ do môi trường DB chưa được xác minh'],
], [3000, 6460]));
children.push(para('Lưu ý về tính trung thực của kết quả: báo cáo này không ghi Pass/Fail giả cho các test chưa chạy. Những lỗi ở mục 3.3 là “candidate bug” được suy ra từ code và phải chuyển thành bug chính thức chỉ sau khi tái hiện bằng test hoặc thao tác thực tế.'));
children.push(heading('3.2. Kế hoạch execution log', HeadingLevel.HEADING_2));
children.push(table(['Nhóm test', 'Số lượng mục tiêu', 'Cách chạy', 'Bằng chứng cần lưu'], [
  ['Unit', '90–100', 'pytest tests/unit', 'Console output, JUnit XML, coverage'],
  ['Integration', '45–50', 'pytest tests/integration với DB test', 'DB snapshot trước/sau, log pytest'],
  ['System', '25–27', 'Flask client hoặc Selenium', 'Screenshot, URL, dữ liệu order/stock'],
  ['Regression', 'Toàn bộ test đã viết', 'Chạy lại sau khi sửa lỗi', 'Execution log lần retest'],
], [1500, 1800, 3700, 2460]));
children.push(heading('3.3. Candidate bug log', HeadingLevel.HEADING_2));
children.push(para('Bảng dưới đây là danh sách vấn đề cần xác minh. Trạng thái “Chưa xác nhận” là bắt buộc vì chưa có bằng chứng thực thi trong môi trường hoàn chỉnh.'));
children.push(table(['Bug ID', 'Tiêu đề', 'Bước tái hiện', 'Expected', 'Actual có thể xảy ra', 'Sev.', 'Status'], bugRows, [1350, 1900, 2200, 1900, 2250, 650, 1210]));
children.push(heading('3.4. Báo cáo kết quả dự kiến', HeadingLevel.HEADING_2));
children.push(para('Sau khi chạy, execution log cần ghi các trường: Test Case ID, ngày chạy, người chạy, môi trường, trạng thái Pass/Fail/Blocked, actual result, bug ID và evidence. Các chỉ số báo cáo gồm: tổng số test, số Pass/Fail/Blocked, pass rate = Pass/Tổng × 100%, số bug theo severity, số bug đã đóng và coverage theo module. Không sử dụng số liệu minh họa thay cho số liệu thực tế.'));
children.push(heading('3.5. Đánh giá rủi ro chất lượng', HeadingLevel.HEADING_2));
children.push(bullet('Rủi ro dữ liệu: chạy test trên database phát triển có thể làm thay đổi sản phẩm, user hoặc order thật.'));
children.push(bullet('Rủi ro giao dịch: lỗi trong checkout hoặc hoàn kho có thể làm stock sai nếu rollback không bao phủ toàn bộ thao tác.'));
children.push(bullet('Rủi ro phân quyền: các route admin phải được kiểm tra bằng request trực tiếp, không chỉ bằng giao diện.'));
children.push(bullet('Rủi ro input: price, quantity, phone và file upload cần test cả kiểu dữ liệu không hợp lệ.'));
children.push(bullet('Rủi ro schema: upgrade_v2.sql tạo suppliers và inventory_logs nhưng các câu lệnh supplier_id trong products đang comment, cần xác minh trước khi test.'));

children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading('CHƯƠNG 4. AUTOMATION TEST', HeadingLevel.HEADING_1));
children.push(heading('4.1. Công cụ sử dụng', HeadingLevel.HEADING_2));
children.push(table(['Công cụ', 'Mục đích', 'Cấu hình/ghi chú'], [
  ['pytest', 'Discovery, fixture, assertion và marker', 'Test source đặt trong tests/'],
  ['Flask test client', 'Gửi request route mà không cần browser', 'Phù hợp unit route và system route-level'],
  ['unittest.mock', 'Cô lập model/database trong unit test', 'Patch tại namespace sử dụng symbol'],
  ['pytest-cov', 'Đo độ bao phủ mã nguồn', 'Xuất terminal và HTML coverage'],
  ['Selenium', 'Tự động hóa browser cho flow đại diện', 'Chỉ dùng sau khi ứng dụng và DB test chạy ổn định'],
  ['JUnit XML', 'Tích hợp kết quả vào công cụ báo cáo', 'pytest --junitxml=report.xml'],
], [1900, 3200, 4160]));
children.push(heading('4.2. Cấu trúc mã automation', HeadingLevel.HEADING_2));
children.push(codeBlock('tests/\n├── conftest.py              # app/client/session fixtures\n├── unit/                    # helper và route test cô lập\n├── integration/             # controller/model/database\n├── system/                  # các flow nghiệp vụ\n└── data/seed_test.sql       # dữ liệu kiểm thử riêng'));
children.push(heading('4.3. Fixture và nguyên tắc cô lập', HeadingLevel.HEADING_2));
children.push(para('Fixture app đặt TESTING=True và SECRET_KEY riêng cho test. Fixture client sử dụng app.test_client(). Fixture user_session và admin_session thiết lập session tương ứng để kiểm tra decorator và các route yêu cầu đăng nhập. Integration fixture cần bổ sung kết nối database test, seed dữ liệu trước test và cleanup sau test; tuyệt đối không trỏ nhầm tới laptop_store phát triển.'));
children.push(heading('4.4. Lệnh chạy chuẩn', HeadingLevel.HEADING_2));
children.push(codeBlock('pytest -q\npytest tests/unit -q\npytest tests/integration -q\npytest --cov=. --cov-report=html --junitxml=report.xml'));
children.push(heading('4.5. Tiêu chí đánh giá automation', HeadingLevel.HEADING_2));
children.push(bullet('Test có ID hoặc tên mô tả được mục tiêu và requirement liên quan.'));
children.push(bullet('Test độc lập, lặp lại được và không phụ thuộc thứ tự chạy.'));
children.push(bullet('Test failure có message đủ rõ để xác định actual/expected.'));
children.push(bullet('Critical path checkout và order state machine có kiểm tra dữ liệu sau transaction.'));
children.push(bullet('Coverage được báo cáo theo module; không dùng coverage cao của helper để che khuất module chưa được kiểm thử.'));
children.push(heading('4.6. Ma trận truy vết', HeadingLevel.HEADING_2));
children.push(table(['Requirement', 'Test case liên quan', 'Phạm vi'], traceRows, [1900, 4700, 2660]));

children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading('KẾT LUẬN', HeadingLevel.HEADING_1));
children.push(para('Báo cáo đã xây dựng khung kiểm thử cho website bán laptop theo ba cấp độ unit, integration và system, đồng thời chuẩn bị hướng automation bằng pytest, Flask test client, mock, coverage và Selenium. Phạm vi được ưu tiên theo mức độ ảnh hưởng nghiệp vụ, trong đó checkout, tồn kho, phân quyền và state machine của đơn hàng là các khu vực có rủi ro cao nhất.'));
children.push(para('Điểm cần hoàn thiện trước khi nộp bản cuối là xác minh schema và kết nối MySQL, chạy toàn bộ test suite, ghi execution log thực tế, tái hiện candidate bug, cập nhật trạng thái bug, chụp evidence và thay thế các trường thông tin còn để trống như tên trường, thành viên và giảng viên.'));
children.push(heading('TÀI LIỆU THAM KHẢO', HeadingLevel.HEADING_1));
children.push(numbered('Mã nguồn dự án LaptopStore Flask, thư mục controllers, models, helpers, templates và static.'));
children.push(numbered('database/laptop_store.sql – schema và dữ liệu mẫu của hệ thống.'));
children.push(numbered('database/upgrade_v2.sql – schema nhà cung cấp và nhật ký tồn kho.'));
children.push(numbered('ISTQB Foundation Level – các kỹ thuật thiết kế kiểm thử và mức độ kiểm thử.'));
children.push(numbered('Tài liệu mẫu UC1_Add New Product và Ví dụ web bán hàng do người học cung cấp.'));

const doc = new Document({
  creator: 'LaptopStore Test Team',
  title: 'Báo cáo kiểm thử phần mềm - Website bán laptop',
  description: 'Báo cáo bài tập lớn môn Kiểm thử phần mềm',
  styles: {
    default: { document: { run: { font: 'Times New Roman', size: 24 }, paragraph: { spacing: { line: 360 } } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', run: { font: 'Times New Roman', size: 34, bold: true, color: navy }, paragraph: { alignment: AlignmentType.CENTER, spacing: { after: 240 } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', run: { font: 'Times New Roman', size: 30, bold: true, color: navy }, paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', run: { font: 'Times New Roman', size: 26, bold: true, color: navy }, paragraph: { spacing: { before: 220, after: 120 }, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', run: { font: 'Times New Roman', size: 24, bold: true, color: '365F91' }, paragraph: { spacing: { before: 160, after: 100 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: 'report-numbering', levels: [{ level: 0, format: 'decimal', text: '%1.', alignment: AlignmentType.START, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: 'report-bullets', levels: [{ level: 0, format: 'bullet', text: '•', style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { margin: { top: 900, right: 900, bottom: 900, left: 1100 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [text('BÁO CÁO KIỂM THỬ LAPTOPSTORE', { size: 18, color: gray, italic: true })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [text('Trang ', { size: 18, color: gray }), PageNumber.CURRENT] })] }) },
    children,
  }],
});

fs.writeFileSync(output, '');
require('docx').Packer.toBuffer(doc).then((buffer) => fs.writeFileSync(output, buffer));
