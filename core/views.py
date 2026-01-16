from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserProfile, RentSession
from .viotp_helper import ViotpHelper
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm, UserUpdateForm
from .models import UserProfile
from django.contrib.messages import get_messages 
from .models import RentSession, DepositTransaction
# Khởi tạo API Helper
api = ViotpHelper()

@login_required
def dashboard(request):
    """Trang chính hiển thị danh sách dịch vụ"""
    
    # 1. Lấy danh sách dịch vụ từ API
    services = api.get_services(country='vn')
    
    # 2. Lấy thông tin ví tiền user
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # 3. Lấy lịch sử thuê
    history = RentSession.objects.filter(user=request.user).order_by('-created_at')[:10]

    # --- [LOGIC MỚI] XỬ LÝ LÀM TRÒN & SỬA GIÁ ---
    if services:
        for sv in services:
            # Lấy giá hiện tại (đang là giá x2 từ helper)
            current_price = sv.get('display_price', 0)
            
            # YÊU CẦU 1: Fix dịch vụ 10k (hoặc cao hơn) -> Về mức giá sàn 4.000đ (gốc 2k)
            if current_price >= 10000:
                sv['display_price'] = 4000
            
            # YÊU CẦU 2: Làm tròn số lẻ (Ví dụ 4.200 -> 4.000)
            else:
                # Công thức: Chia 1000 lấy phần nguyên, rồi nhân lại 1000
                # Ví dụ: 4200 // 1000 = 4  --> 4 * 1000 = 4000
                sv['display_price'] = (current_price // 1000) * 1000
                
            # Đảm bảo giá không bao giờ bằng 0 (nếu lỡ làm tròn sai)
            if sv['display_price'] < 1000:
                sv['display_price'] = 1000
    # ---------------------------------------------

    return render(request, 'dashboard.html', {
        'services': services,
        'profile': profile,
        'history': history
    })
@login_required
def rent_service(request, service_id, price):
    """Xử lý khi bấm nút Thuê"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    sell_price = int(price)
    
    # --- THÊM DÒNG NÀY: Lấy tên dịch vụ từ URL ---
    # Nếu không có tên thì mới dùng tạm "Dịch vụ {id}"
    service_name_input = request.GET.get('name', f"Dịch vụ {service_id}") 
    # ---------------------------------------------

    # 1. Kiểm tra tiền
    if profile.balance < sell_price:
        return JsonResponse({'status': 'error', 'message': 'Tài khoản không đủ tiền!'})

    # 2. Gọi API thuê số thực tế
    resp = api.request_number(service_id)
    
    if resp and resp.get('status_code') == 200:
        data = resp['data']
        
        # 3. Trừ tiền và Lưu lịch sử
        profile.balance -= sell_price
        profile.save()

        RentSession.objects.create(
            user=request.user,
            request_id=data['request_id'],
            
            # --- SỬA DÒNG NÀY: Dùng biến service_name_input đã lấy ở trên ---
            service_name=service_name_input, 
            # ----------------------------------------------------------------
            
            phone_number=data['phone_number'],
            original_price=sell_price / 2,
            sell_price=sell_price,
            status="Waiting"
        )
        return JsonResponse({
            'status': 'success', 
            'phone': data['phone_number'], 
            'req_id': data['request_id']
        })
    else:
        msg = resp.get('message', 'Lỗi kết nối API') if resp else "Lỗi kết nối"
        return JsonResponse({'status': 'error', 'message': msg})
@login_required
def check_otp(request):
    """API kiểm tra OTP và Tự động hoàn tiền nếu lỗi"""
    req_id = request.GET.get('req_id')
    
    # 1. Gọi API nhà mạng kiểm tra
    otp_resp = api.get_otp(req_id)
    
    if otp_resp and 'data' in otp_resp:
        api_data = otp_resp['data']
        api_status = api_data.get('Status')
        code = api_data.get('Code')

        # 2. Lấy session từ DB
        session = RentSession.objects.filter(request_id=req_id).first()
        
        if session:
            # --- TRƯỜNG HỢP 1: THÀNH CÔNG (Có Code) ---
            if api_status == 1: 
                if session.status != 'Success': # Tránh cập nhật trùng
                    session.otp_code = code
                    session.status = "Success"
                    session.save()
                return JsonResponse({'status': 'found', 'code': code})
            
            # --- TRƯỜNG HỢP 2: HẾT HẠN / HỦY (HOÀN TIỀN TẠI ĐÂY) ---
            elif api_status == 2: 
                if session.status == 'Waiting': # QUAN TRỌNG: Chỉ hoàn nếu đang chờ
                    # A. Cộng lại tiền cho khách
                    user_profile = session.user.profile
                    user_profile.balance += session.sell_price
                    user_profile.save()
                    
                    # B. Đổi trạng thái đơn thành Expired
                    session.status = "Expired"
                    session.save()
                    
                    print(f"Đã hoàn {session.sell_price}đ cho đơn {req_id}") # Log kiểm tra
                
                return JsonResponse({'status': 'expired'})

    return JsonResponse({'status': 'waiting'})
@login_required
def history(request):
    """Trang lịch sử - Tự động đồng bộ và Hoàn tiền"""
    
    # 1. Lấy tất cả đơn đang treo (Waiting) của user này
    pending_sessions = RentSession.objects.filter(user=request.user, status='Waiting')
    
    user_profile = request.user.profile
    has_refund = False # Cờ đánh dấu xem có đơn nào được hoàn không

    for session in pending_sessions:
        try:
            # Hỏi trạng thái thật từ API
            resp = api.get_otp(session.request_id)
            if resp and 'data' in resp:
                api_status = resp['data']['Status']
                
                # NẾU ĐƠN ĐÃ BỊ HỦY/HẾT HẠN -> HOÀN TIỀN
                if api_status == 2:
                    user_profile.balance += session.sell_price # Cộng tiền
                    session.status = 'Expired' # Đổi trạng thái
                    session.save()
                    has_refund = True # Đánh dấu là có thay đổi tiền
                
                # NẾU ĐƠN THÀNH CÔNG MÀ QUÊN CẬP NHẬT
                elif api_status == 1:
                    session.status = 'Success'
                    session.otp_code = resp['data']['Code']
                    session.save()
                    
        except Exception as e:
            print(f"Lỗi đồng bộ đơn {session.request_id}: {e}")

    # 2. Nếu có hoàn tiền, cần lưu lại UserProfile
    if has_refund:
        user_profile.save()
        messages.success(request, "Hệ thống đã tự động hoàn tiền các đơn hàng lỗi/hết hạn!")

    # 3. Hiển thị dữ liệu ra (Lúc này các đơn Expired đã được cập nhật xong)
    history_data = RentSession.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'history.html', {
        'history': history_data
    })
def register_view(request):
    """Xử lý Đăng ký tài khoản"""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # --- QUAN TRỌNG: Tạo ví tiền 0đ ngay khi đăng ký ---
            UserProfile.objects.create(user=user, balance=0) 
            # ---------------------------------------------------
            
            login(request, user) # Tự động đăng nhập luôn sau khi đăng ký
            messages.success(request, f"Chào mừng {user.username}! Bạn đã đăng ký thành công.")
            return redirect('dashboard') # Chuyển hướng về trang chủ
        else:
            messages.error(request, "Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    """Xử lý Đăng nhập"""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Xin chào {username}.")
                return redirect('dashboard')
            else:
                messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
    else:
        form = AuthenticationForm()
        # Thêm class bootstrap cho form login mặc định
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-control mb-3'})

    return render(request, 'login.html', {'form': form})
def logout_view(request):
    """Xử lý Đăng xuất và xóa tin nhắn cũ"""
    
    # 1. Xóa sạch các tin nhắn cũ đang tồn đọng (nếu có)
    storage = get_messages(request)
    for _ in storage:
        pass  # Vòng lặp này có tác dụng "đọc và hủy" hết tin nhắn cũ
        
    # 2. Thực hiện đăng xuất
    logout(request)
    
    # 3. Chỉ thêm tin nhắn mới này thôi
    messages.info(request, "Bạn đã đăng xuất thành công.")
    
    return redirect('login')
@login_required
def profile_view(request):
    """Trang thông tin cá nhân & Thống kê"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Tính toán thống kê
    total_rented = RentSession.objects.filter(user=request.user).count()
    last_rented = RentSession.objects.filter(user=request.user).order_by('-created_at').first()
    last_date = last_rented.created_at if last_rented else None

    # Xử lý Form cập nhật
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user, profile=profile)
        if form.is_valid():
            user = form.save()
            # Lưu số điện thoại vào profile
            profile.phone_number = form.cleaned_data.get('phone_number')
            profile.save()
            messages.success(request, "Cập nhật thông tin thành công!")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user, profile=profile)

    return render(request, 'profile.html', {
        'form': form,
        'profile': profile,
        'total_rented': total_rented,
        'last_date': last_date
    })

@login_required
def deposit_view(request):
    """Trang nạp tiền - Hiển thị QR Code"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # CẤU HÌNH THÔNG TIN NGÂN HÀNG CỦA BẠN TẠI ĐÂY
    BANK_ID = "MB" # Ví dụ MBBank, TCB, VCB...
    ACCOUNT_NO = "0973457296" 
    ACCOUNT_NAME = "TRAN QUOC VIET"
    
    # Nội dung chuyển khoản: NAP + Username
    memo = f"NAP TIEN TK {request.user.username.upper()}"
    
    # Link tạo QR tự động từ VietQR (Không cần API Key)
    qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-print.png?addInfo={memo}"

    return render(request, 'deposit.html', {
        'bank_name': "MB BANK", # Tên hiển thị
        'acc_no': ACCOUNT_NO,
        'acc_name': ACCOUNT_NAME,
        'memo': memo,
        'qr_url': qr_url,
        'profile': profile
    })

@login_required
def deposit_history(request):
    """Lịch sử nạp tiền"""
    transactions = DepositTransaction.objects.filter(user=request.user).order_by('-created_at')
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    return render(request, 'deposit_history.html', {
        'transactions': transactions,
        'profile': profile
    })