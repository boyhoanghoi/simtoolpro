import requests
from datetime import datetime, timedelta
class ViotpHelper:
    def __init__(self):
        # KHUYẾN CÁO: Nên để Token trong biến môi trường (.env) để bảo mật
        self.token = "935ee0f577cb44e983be5606c2af1e24"
        self.base_url = "https://api.viotp.com"

    def get_services(self, country='vn'):
        url = f"{self.base_url}/service/getv2"
        params = {'token': self.token, 'country': country}
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data['status_code'] == 200:
                services = data['data']
                # --- LOGIC X2 GIÁ Ở ĐÂY ---
                for s in services:
                    s['original_price'] = s['price'] # Lưu giá gốc để tính toán nếu cần
                    s['display_price'] = s['price'] * 2 # Giá hiển thị cho khách
                return services
            return []
        except:
            return []

    def request_number(self, service_id):
        # Gọi API thuê số
        url = f"{self.base_url}/request/getv2"
        params = {'token': self.token, 'serviceId': service_id}
        try:
            response = requests.get(url, params=params)
            return response.json()
        except:
            return None

    def get_otp(self, request_id):
        url = f"{self.base_url}/session/getv2"
        params = {'token': self.token, 'requestId': request_id}
        try:
            response = requests.get(url, params=params)
            return response.json()
        except:
            return None
    def get_history(self):
        """Lấy lịch sử thuê số trong 7 ngày gần nhất"""
        url = f"{self.base_url}/session/historyv2"
        
        # Lấy ngày hiện tại và 7 ngày trước
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        params = {
            'token': self.token,
            'limit': 50, # Lấy 50 giao dịch gần nhất
            'fromDate': from_date,
            'toDate': to_date
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data.get('status_code') == 200:
                history_list = data.get('data', [])
                
                # XỬ LÝ DỮ LIỆU TRƯỚC KHI TRẢ VỀ
                for item in history_list:
                    # 1. Nhân đôi giá tiền để khớp với web của bạn
                    item['display_price'] = item['Price'] * 2 
                    
                    # 2. Xử lý trạng thái cho đẹp
                    if item['Status'] == 1:
                        item['status_text'] = "Hoàn thành"
                        item['status_class'] = "success" # Màu xanh
                    else:
                        item['status_text'] = "Hết hạn/Hủy"
                        item['status_class'] = "secondary" # Màu xám

                return history_list
            return []
        except Exception as e:
            print(f"Lỗi lấy lịch sử: {e}")
            return []