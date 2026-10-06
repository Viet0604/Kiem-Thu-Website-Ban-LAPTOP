"""Unit test cho OrderModel.update_status — map UT-ORD-01 và UT-ORD-02."""
from unittest.mock import MagicMock, patch


def _mock_cursor_with_fetchone(fetchone_val, fetchall_val=None, rowcount=0):
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=cur)
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = fetchone_val
    cur.fetchall.return_value = fetchall_val or []
    cur.lastrowid = 1
    cur.rowcount = rowcount
    cur.execute = MagicMock()
    return cur


def _mock_db(cur):
    db = MagicMock()
    db.cursor.return_value = cur
    db.commit = MagicMock()
    db.rollback = MagicMock()
    return db


class TestOrderUpdateStatus:
    @patch("models.order.get_db")
    def test_valid_transition_pending_to_processing(self, mock_get_db):
        """UT-ORD-01: cho phép chuyển trạng thái hợp lệ pending -> processing."""
        from models.order import OrderModel
        cur = _mock_cursor_with_fetchone({"status": "pending"}, [{"product_id": 1, "quantity": 2}])
        mock_get_db.return_value = _mock_db(cur)

        ok, msg = OrderModel.update_status(1, "processing")

        assert ok is True
        assert "thành công" in msg.lower()

    @patch("models.order.get_db")
    def test_invalid_transition_delivered_to_pending(self, mock_get_db):
        """UT-ORD-02: từ chối chuyển trạng thái không hợp lệ delivered -> pending."""
        from models.order import OrderModel
        cur = _mock_cursor_with_fetchone({"status": "delivered"})
        mock_get_db.return_value = _mock_db(cur)

        ok, msg = OrderModel.update_status(1, "pending")

        assert ok is False
        assert "không thể chuyển" in msg.lower()
