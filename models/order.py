from models.db import get_db

class OrderModel:
    @staticmethod
    def create_order(user_id, data, cart_items):
        db = get_db()
        try:
            with db.cursor() as cursor:
                # 1. Kiểm tra tồn kho trước
                for item in cart_items.values():
                    cursor.execute("SELECT name, stock, is_active FROM products WHERE id = %s FOR UPDATE", (item['id'],))
                    product = cursor.fetchone()
                    
                    if not product or product['is_active'] == 0:
                        raise ValueError(f"Sản phẩm {item['name']} không còn kinh doanh.")
                    if product['stock'] < item['quantity']:
                        raise ValueError(f"Sản phẩm {product['name']} không đủ tồn kho (Còn {product['stock']}).")

                # 2. Tạo đơn hàng
                query_order = """
                    INSERT INTO orders 
                    (user_id, total_amount, receiver_name, receiver_phone, receiver_address, payment_method, note, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
                """
                cursor.execute(query_order, (
                    user_id, data['total_amount'], data['receiver_name'], 
                    data['receiver_phone'], data['receiver_address'], 
                    data['payment_method'], data.get('note', '')
                ))
                order_id = cursor.lastrowid
                
                # 3. Thêm chi tiết đơn hàng & trừ tồn kho
                for item in cart_items.values():
                    # Thêm chi tiết (Cần truyền name theo CSDL)
                    cursor.execute("""
                        INSERT INTO order_details (order_id, product_id, product_name, quantity, price)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, item['id'], item['name'], item['quantity'], item['price']))
                    
                    # Trừ tồn kho
                    cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (item['quantity'], item['id']))
                
                db.commit()
                return order_id
        except ValueError as ve:
            db.rollback()
            return {"error": str(ve)}
        except Exception as e:
            db.rollback()
            print(f"Lỗi tạo đơn hàng: {e}")
            return {"error": "Lỗi hệ thống khi tạo đơn hàng."}

    @staticmethod
    def find_by_id(order_id, user_id=None):
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT o.*, u.fullname as user_fullname, u.email as user_email
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.id = %s
            """
            params = [order_id]
            if user_id:
                query += " AND o.user_id = %s"
                params.append(user_id)
                
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def get_by_user(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            return cursor.fetchall()

    @staticmethod
    def get_all(status=None):
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT o.*, u.fullname as user_fullname
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
            """
            params = []
            if status:
                query += " WHERE o.status = %s"
                params.append(status)
            query += " ORDER BY o.created_at DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_order_details(order_id):
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT od.*, p.name as product_name, p.image 
                FROM order_details od
                JOIN products p ON od.product_id = p.id
                WHERE od.order_id = %s
            """
            cursor.execute(query, (order_id,))
            return cursor.fetchall()

    @staticmethod
    def update_status(order_id, new_status):
        db = get_db()
        try:
            with db.cursor() as cursor:
                # Lấy trạng thái hiện tại
                cursor.execute("SELECT status FROM orders WHERE id = %s FOR UPDATE", (order_id,))
                order = cursor.fetchone()
                if not order:
                    return False, "Không tìm thấy đơn hàng."
                    
                old_status = order['status']
                
                # Validate State Machine
                valid_transitions = {
                    'pending': ['processing', 'cancelled'],
                    'processing': ['shipping', 'cancelled'],
                    'shipping': ['delivered'],
                    'delivered': [],
                    'cancelled': []
                }
                
                if new_status not in valid_transitions.get(old_status, []):
                    return False, f"Không thể chuyển trạng thái từ '{old_status}' sang '{new_status}'."
                
                # Update status
                cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
                
                # Nếu hủy đơn, cần hoàn trả tồn kho
                if new_status == 'cancelled' and old_status != 'cancelled':
                    cursor.execute("SELECT product_id, quantity FROM order_details WHERE order_id = %s", (order_id,))
                    details = cursor.fetchall()
                    for item in details:
                        cursor.execute("UPDATE products SET stock = stock + %s WHERE id = %s", (item['quantity'], item['product_id']))
                        
                db.commit()
                return True, "Cập nhật thành công."
        except Exception as e:
            db.rollback()
            return False, f"Lỗi: {str(e)}"

    @staticmethod
    def count_all():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM orders")
            result = cursor.fetchone()
            return result['total'] if result else 0

    @staticmethod
    def count_by_status(status):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM orders WHERE status = %s", (status,))
            result = cursor.fetchone()
            return result['total'] if result else 0

    @staticmethod
    def get_total_revenue():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT SUM(total_amount) as total FROM orders WHERE status = 'delivered'")
            result = cursor.fetchone()
            return result['total'] if result and result['total'] else 0

    @staticmethod
    def get_revenue_by_month(limit=12):
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT 
                    DATE_FORMAT(created_at, '%%m/%%Y') as month,
                    SUM(total_amount) as revenue
                FROM orders
                WHERE status = 'delivered'
                GROUP BY DATE_FORMAT(created_at, '%%m/%%Y'), DATE_FORMAT(created_at, '%%Y%%m')
                ORDER BY DATE_FORMAT(created_at, '%%Y%%m') DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            # Đảo ngược để hiển thị từ cũ tới mới trên biểu đồ
            result = list(cursor.fetchall())
            result.reverse()
            return result
