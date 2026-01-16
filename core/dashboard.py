from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import RentSession
from django.contrib.auth.models import User

def dashboard_callback(request, context):
    print(">>> Dashboard callback is being executed!")
    today = timezone.now().date()
    
    # Tính toán số liệu thực tế
    total_revenue = RentSession.objects.filter(status='Success').aggregate(Sum('sell_price'))['sell_price__sum'] or 0
    total_users = User.objects.count()
    today_orders = RentSession.objects.filter(created_at__date=today).count()

    # Tạo dữ liệu biểu đồ 7 ngày
    labels = []
    data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        rev = RentSession.objects.filter(status='Success', created_at__date=day).aggregate(Sum('sell_price'))['sell_price__sum'] or 0
        labels.append(day.strftime('%d/%m'))
        data.append(rev)

    context.update({
        "kpi": [
            {"title": "Tổng Doanh Thu", "metric": f"{total_revenue:,.0f}đ", "footer": "Toàn thời gian"},
            {"title": "Người dùng", "metric": total_users, "footer": "Tổng thành viên"},
            {"title": "Đơn hôm nay", "metric": today_orders, "footer": "Số lượt thuê số"},
        ],
        "charts": [
            {
                "type": "line",
                "labels": labels,
                "datasets": [{"data": data}]
            }
        ]
    })
    return context