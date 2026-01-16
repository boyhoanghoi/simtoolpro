from django.db import models
from django.contrib.auth.models import User

# 1. Mở rộng User để có thêm ví tiền (Balance)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.IntegerField(default=0, verbose_name="Số dư")
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name="Số điện thoại")
    def __str__(self):
        return f"{self.user.username} - {self.balance:,}đ"

    class Meta:
        verbose_name = "Ví người dùng"
        verbose_name_plural = "Quản lý ví tiền"

# 2. Lưu lịch sử thuê SIM
class RentSession(models.Model):
    # Định nghĩa các trạng thái để tránh gõ sai
    STATUS_CHOICES = [
        ('Waiting', 'Đang chờ'),
        ('Success', 'Thành công'),
        ('Expired', 'Hết hạn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rent_history')
    request_id = models.CharField(max_length=50, verbose_name="Mã Request ID") 
    service_name = models.CharField(max_length=100, verbose_name="Tên dịch vụ")
    phone_number = models.CharField(max_length=20, verbose_name="Số điện thoại")
    
    original_price = models.IntegerField(default=0, help_text="Giá gốc nhập vào")
    sell_price = models.IntegerField(default=0, help_text="Giá bán cho khách")
    
    otp_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="Mã OTP")
    sms_content = models.TextField(null=True, blank=True, verbose_name="Nội dung tin nhắn") # Thêm trường này nếu muốn lưu full tin nhắn
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Waiting", verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")

    def __str__(self):
        return f"{self.user.username} - {self.phone_number} - {self.otp_code}"

    class Meta:
        ordering = ['-created_at'] # Tự động sắp xếp mới nhất lên đầu
        verbose_name = "Lịch sử thuê số"
        verbose_name_plural = "Quản lý thuê số"
class DepositTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name="Số tiền nạp")
    bank_name = models.CharField(max_length=50, default="Techcombank")
    content = models.CharField(max_length=50, verbose_name="Nội dung CK")
    balance_after = models.IntegerField(default=0, verbose_name="Số dư sau biến động")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} nạp {self.amount}"