from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('rent/<int:service_id>/<int:price>/', views.rent_service, name='rent'),
    path('check-otp/', views.check_otp, name='check_otp'),
    path('history/', views.history, name='history'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('deposit-history/', views.deposit_history, name='deposit_history'),
]