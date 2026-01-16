from django import template
from django.db.models import Sum
from django.contrib.auth.models import User
from core.models import RentSession
from django.utils import timezone
from datetime import timedelta
import json

register = template.Library()

@register.simple_tag
def get_dashboard_data():
    # 1. Tính toán KPI
    total_users = User.objects.count()
    total_orders = RentSession.objects.count()
    total_revenue = RentSession.objects.filter(status='Success').aggregate(Sum('sell_price'))['sell_price__sum'] or 0
    
    # 2. Tính biểu đồ 7 ngày
    today = timezone.now()
    labels = []
    data = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%d/%m')
        
        daily_rev = RentSession.objects.filter(
            status='Success',
            created_at__date=day.date()
        ).aggregate(Sum('sell_price'))['sell_price__sum'] or 0
        
        labels.append(day_str)
        data.append(int(daily_rev)) # Chuyển về số nguyên
        
    return {
        'users': total_users,
        'orders': total_orders,
        'revenue': f"{total_revenue:,.0f}",
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data),
    }