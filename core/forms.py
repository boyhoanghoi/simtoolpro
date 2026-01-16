from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Form Đăng ký
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "email") # Các trường muốn hiển thị

    # Thêm class CSS của Bootstrap để form đẹp hơn
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            # Dòng này thêm class 'form-control' cho mọi ô input
            self.fields[field].widget.attrs.update({'class': 'form-control'})
class UserUpdateForm(forms.ModelForm):
    # Thêm trường phone từ UserProfile vào form
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=False, label="Họ tên", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'email']

    def __init__(self, *args, **kwargs):
        # Lấy phone từ profile để hiển thị ban đầu
        self.profile = kwargs.pop('profile', None)
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if self.profile:
            self.fields['phone_number'].initial = self.profile.phone_number