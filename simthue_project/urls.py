from django.contrib import admin
from django.urls import path, include # Nhớ thêm include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # Chuyển hướng trang chủ về app core
]