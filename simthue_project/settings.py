import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-f*gyx(g9968lo$ah^dcy-f-0y25u4qgmo@vlg2i^w4*4z9poad'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
# Application definition

# Cấu hình giao diện Unfold
UNFOLD = {
    "SITE_TITLE": "SIM TOOL PRO ADMIN",
    "SITE_HEADER": "QUẢN TRỊ HỆ THỐNG",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "core.dashboard.dashboard_callback", # Hàm xử lý dữ liệu biểu đồ
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "67 97 238",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Quản lý kinh doanh",
                "items": [
                    {
                        "title": "Danh sách đơn thuê",
                        "icon": "phone",
                        "link": "/admin/core/rentsession/",
                    },
                    {
                        "title": "Lịch sử nạp tiền",
                        "icon": "account_balance_wallet",
                        "link": "/admin/core/deposittransaction/",
                    },
                ],
            },
            {
                "title": "Hệ thống",
                "items": [
                    {
                        "title": "Quản lý Users",
                        "icon": "people",
                        "link": "/admin/auth/user/",
                    },
                ],
            },
        ],
    },
}

INSTALLED_APPS = [
    "unfold",  
    "unfold.contrib.filters",  
    "unfold.contrib.forms",    
    "unfold.contrib.import_export", 
    "core",  # Đặt core ở đây để ghi đè template của admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'simthue_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # QUAN TRỌNG: Chỉ định thư mục templates gốc
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'simthue_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth Redirects
LOGIN_URL = 'login' 
LOGIN_REDIRECT_URL = 'dashboard'