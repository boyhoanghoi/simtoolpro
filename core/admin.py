from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, RentSession, DepositTransaction
from unfold.admin import ModelAdmin
from django.utils.html import format_html

# 1. Quản lý Ví người dùng
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserAdmin(BaseUserAdmin, ModelAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'display_balance', 'is_staff')
    
    def display_balance(self, instance):
        return f"{instance.profile.balance:,} đ"
    display_balance.short_description = 'Số dư ví'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 2. Quản lý Đơn thuê (Tối ưu hiển thị Badge)
@admin.register(RentSession)
class RentSessionAdmin(ModelAdmin):
    list_display = ('id', 'user', 'service_name', 'phone_number', 'sell_price', 'otp_badge', 'status_badge', 'created_at')
    list_filter = ('status', 'service_name', 'created_at')
    search_fields = ('user__username', 'phone_number', 'request_id')
    readonly_fields = ('request_id', 'created_at')

    def otp_badge(self, obj):
        if obj.otp_code:
            return format_html('<span style="font-family: monospace; font-weight: bold; color: #10b981;">{}</span>', obj.otp_code)
        return "-"
    otp_badge.short_description = "OTP"

    def status_badge(self, obj):
        colors = {
            "Success": "background: #dcfce7; color: #166534;", # Xanh lá
            "Waiting": "background: #fef9c3; color: #854d0e;", # Vàng
            "Expired": "background: #fee2e2; color: #991b1b;"  # Đỏ
        }
        style = colors.get(obj.status, "background: #f3f4f6; color: #374151;")
        return format_html('<span style="{} padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: bold;">{}</span>', style, obj.get_status_display())
    status_badge.short_description = "Trạng thái"

# 3. Quản lý Nạp tiền
@admin.register(DepositTransaction)
class DepositTransactionAdmin(ModelAdmin):
    list_display = ('user', 'amount_display', 'bank_name', 'content', 'created_at')
    list_filter = ('bank_name', 'created_at')
    
    def amount_display(self, obj):
        return format_html('<span style="color: #10b981; font-weight: bold;">+ {:,} đ</span>', obj.amount)
    amount_display.short_description = "Số tiền"