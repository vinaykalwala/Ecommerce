from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
import random
import string
from .forms import (
    CustomerSignupForm,
    AdminSignupForm,
    SuperuserSignupForm,
    UserUpdateForm,
    UserProfileForm,
    AddressForm,
    OTPVerificationForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from .models import Address, UserProfile, User, OTPVerification, LoginAttempt
from PIL import Image, ImageDraw, ImageFont
import io
from django.http import HttpResponse
import hashlib
import time

# Helper functions
def is_superuser(user):
    return user.is_authenticated and user.user_type == 'superuser'

def is_admin(user):
    return user.is_authenticated and (user.user_type == 'admin' or user.user_type == 'superuser')

def send_otp_email(destination, otp_code, otp_type):
    """Send OTP via email"""
    subject = f'Your OTP for {otp_type} - E-commerce App'
    message = f"""
    Hello,
    
    Your OTP for {otp_type} is: {otp_code}
    
    This OTP is valid for 10 minutes.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    E-commerce Team
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [destination],
        fail_silently=False,
    )

def send_otp_sms(mobile_number, otp_code, otp_type):
    """Send OTP via SMS - Implement with your SMS provider"""
    # Example with Twilio - you'll need to add twilio package
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(
    #     body=f'Your OTP for {otp_type} is: {otp_code}',
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=mobile_number
    # )
    pass

class SimpleCaptcha:
    def __init__(self):
        self.captcha_text = ''.join(random.choices(string.digits + string.ascii_uppercase, k=6))
        self.captcha_key = hashlib.md5(f"{self.captcha_text}{time.time()}".encode()).hexdigest()
    
    def generate_image(self):
        image = Image.new('RGB', (200, 60), color='white')
        draw = ImageDraw.Draw(image)
        
        for _ in range(1000):
            x = random.randint(0, 200)
            y = random.randint(0, 60)
            draw.point((x, y), fill='black')
        
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        draw.text((20, 10), self.captcha_text, fill='black', font=font)
        
        for _ in range(5):
            x1 = random.randint(0, 200)
            y1 = random.randint(0, 60)
            x2 = random.randint(0, 200)
            y2 = random.randint(0, 60)
            draw.line((x1, y1, x2, y2), fill='gray')
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()

def generate_captcha(request):
    captcha = SimpleCaptcha()
    request.session['captcha_text'] = captcha.captcha_text
    request.session['captcha_key'] = captcha.captcha_key
    return HttpResponse(captcha.generate_image(), content_type='image/png')

# Signup Views
def customer_signup_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            
            # Generate and send OTP
            otp_code = OTPVerification.generate_otp()
            OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                otp_type='signup',
                destination=user.email
            )
            send_otp_email(user.email, otp_code, 'signup')
            
            request.session['pending_verification_user_id'] = user.id
            messages.success(request, 'Account created! Please verify your email with OTP.')
            return redirect('verify_otp', otp_type='signup')
    else:
        form = CustomerSignupForm()
    
    return render(request, 'accounts/customer_signup.html', {'form': form, 'title': 'Customer Signup'})

def admin_signup_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            
            otp_code = OTPVerification.generate_otp()
            OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                otp_type='signup',
                destination=user.email
            )
            send_otp_email(user.email, otp_code, 'signup')
            
            request.session['pending_verification_user_id'] = user.id
            messages.success(request, 'Admin account created! Please verify your email with OTP.')
            return redirect('verify_otp', otp_type='signup')
    else:
        form = AdminSignupForm()
    
    return render(request, 'accounts/admin_signup.html', {'form': form, 'title': 'Admin Signup'})

def superuser_signup_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = SuperuserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            
            otp_code = OTPVerification.generate_otp()
            OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                otp_type='signup',
                destination=user.email
            )
            send_otp_email(user.email, otp_code, 'signup')
            
            request.session['pending_verification_user_id'] = user.id
            messages.success(request, 'Superuser account created! Please verify your email with OTP.')
            return redirect('verify_otp', otp_type='signup')
    else:
        form = SuperuserSignupForm()
    
    return render(request, 'accounts/superuser_signup.html', {'form': form, 'title': 'Superuser Signup'})

def verify_otp_view(request, otp_type):
    user_id = request.session.get('pending_verification_user_id')
    if not user_id and request.user.is_authenticated:
        user_id = request.user.id
    
    if not user_id:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('login')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            
            try:
                otp = OTPVerification.objects.filter(
                    user=user,
                    otp_code=otp_code,
                    otp_type=otp_type,
                    is_used=False
                ).latest('created_at')
                
                if otp.is_valid():
                    otp.is_used = True
                    otp.save()
                    
                    if otp_type == 'signup':
                        user.is_verified = True
                        user.email_verified = True
                        user.save()
                        login(request, user)
                        messages.success(request, f'Email verified successfully! Welcome {user.first_name}!')
                        return redirect('profile')
                    
                    elif otp_type == 'forgot_password':
                        request.session['reset_password_user_id'] = user.id
                        messages.success(request, 'OTP verified! Please set your new password.')
                        return redirect('reset_password')
                    
                    elif otp_type == 'change_password':
                        request.session['change_password_verified'] = True
                        messages.success(request, 'OTP verified! You can now change your password.')
                        return redirect('change_password_with_otp')
                else:
                    messages.error(request, 'OTP has expired! Please request a new one.')
            except OTPVerification.DoesNotExist:
                messages.error(request, 'Invalid OTP! Please try again.')
    else:
        form = OTPVerificationForm()
    
    # Handle resend OTP
    if request.GET.get('resend'):
        otp_code = OTPVerification.generate_otp()
        OTPVerification.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type=otp_type,
            destination=user.email
        )
        send_otp_email(user.email, otp_code, otp_type)
        messages.success(request, 'New OTP sent to your email!')
    
    return render(request, 'accounts/verify_otp.html', {
        'form': form,
        'otp_type': otp_type,
        'destination': user.email,
        'user_id': user.id
    })

def login_view(request):
    # If already logged in
    if request.user.is_authenticated:
        if request.user.user_type == 'customer':
            return redirect('home')
        else:
            return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        captcha_input = request.POST.get('captcha', '').upper()
        captcha_session = request.session.get('captcha_text', '')

        if captcha_input != captcha_session:
            messages.error(request, 'Invalid captcha!')

        elif form.is_valid():
            login_input = form.cleaned_data['login_input']
            password = form.cleaned_data['password']

            user = None

            # Login with Email
            try:
                user_obj = User.objects.get(email=login_input)
                user = authenticate(
                    request,
                    username=user_obj.email,
                    password=password
                )
            except User.DoesNotExist:
                pass

            # Login with Username
            if not user:
                try:
                    user_obj = User.objects.get(username=login_input)
                    user = authenticate(
                        request,
                        username=user_obj.email,
                        password=password
                    )
                except User.DoesNotExist:
                    pass

            # Login with Mobile Number
            if not user and login_input.isdigit():
                try:
                    user_obj = User.objects.get(
                        mobile_number=login_input
                    )
                    user = authenticate(
                        request,
                        username=user_obj.email,
                        password=password
                    )
                except User.DoesNotExist:
                    pass

            # Get IP Address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Save Login Attempt
            LoginAttempt.objects.create(
                username=login_input,
                ip_address=ip_address,
                is_successful=bool(user)
            )

            if user:

                if not user.is_verified:
                    messages.error(
                        request,
                        'Please verify your email first!'
                    )

                    request.session[
                        'pending_verification_user_id'
                    ] = user.id

                    return redirect(
                        'verify_otp',
                        otp_type='signup'
                    )

                login(request, user)

                user.last_login_ip = ip_address
                user.save()

                messages.success(
                    request,
                    f'Welcome back, {user.first_name}!'
                )

                # Redirect to requested page
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)

                # Redirect based on role
                if user.user_type == 'customer':
                    return redirect('home')

                elif user.user_type in ['admin', 'superuser']:
                    return redirect('dashboard')

                return redirect('home')

            else:
                messages.error(
                    request,
                    'Invalid credentials! Please check your email, username, phone number, and password.'
                )

    else:
        form = LoginForm()

        captcha = SimpleCaptcha()
        request.session['captcha_text'] = captcha.captcha_text
        request.session['captcha_key'] = captcha.captcha_key

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )
    
def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            contact_info = form.cleaned_data['contact_info']
            
            user = None
            if '@' in contact_info:
                try:
                    user = User.objects.get(email=contact_info)
                except User.DoesNotExist:
                    pass
            elif contact_info.isdigit():
                try:
                    user = User.objects.get(mobile_number=contact_info)
                except User.DoesNotExist:
                    pass
            
            if user:
                otp_code = OTPVerification.generate_otp()
                OTPVerification.objects.create(
                    user=user,
                    otp_code=otp_code,
                    otp_type='forgot_password',
                    destination=contact_info if '@' in contact_info else user.email
                )
                
                if '@' in contact_info:
                    send_otp_email(contact_info, otp_code, 'forgot_password')
                else:
                    send_otp_sms(contact_info, otp_code, 'forgot_password')
                
                request.session['pending_verification_user_id'] = user.id
                messages.success(request, 'OTP sent to your registered contact!')
                return redirect('verify_otp', otp_type='forgot_password')
            else:
                messages.error(request, 'No user found with this contact information!')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})

def reset_password_view(request):
    user_id = request.session.get('reset_password_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('forgot_password')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            
            del request.session['reset_password_user_id']
            
            messages.success(request, 'Password reset successful! Please login with your new password.')
            return redirect('login')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form})

@login_required
def change_password_request_view(request):
    if request.method == 'POST':
        otp_code = OTPVerification.generate_otp()
        OTPVerification.objects.create(
            user=request.user,
            otp_code=otp_code,
            otp_type='change_password',
            destination=request.user.email
        )
        send_otp_email(request.user.email, otp_code, 'change_password')
        
        messages.success(request, 'OTP sent to your email!')
        return redirect('verify_otp', otp_type='change_password')
    
    return render(request, 'accounts/change_password_request.html')

@login_required
def change_password_with_otp_view(request):
    if not request.session.get('change_password_verified'):
        messages.error(request, 'Please verify OTP first!')
        return redirect('change_password_request')
    
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            
            del request.session['change_password_verified']
            
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    addresses = request.user.addresses.all()
    
    context = {
        'profile': profile,
        'address_count': addresses.count(),
        'addresses': addresses[:3]
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def address_list_view(request):
    addresses = request.user.addresses.all()
    paginator = Paginator(addresses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/address_list.html', {'addresses': page_obj})

@login_required
def add_address_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('address_list')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Add Address'})

@login_required
def edit_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Edit Address'})

@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('address_list')
    
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})

@login_required
def set_default_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, 'Default address set successfully!')
    return redirect('address_list')

@login_required
@user_passes_test(is_admin)
def user_management_view(request):
    users = User.objects.all().order_by('-date_joined')
    user_type = request.GET.get('user_type')
    
    if user_type:
        users = users.filter(user_type=user_type)
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/user_management.html', {'users': page_obj})

@login_required
@user_passes_test(is_superuser)
def edit_user_permissions_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        
        if user_type in ['customer', 'admin', 'superuser']:
            user.user_type = user_type
            if user_type == 'superuser':
                user.is_superuser = True
                user.is_staff = True
            elif user_type == 'admin':
                user.is_staff = True
                user.is_superuser = False
            else:
                user.is_staff = False
                user.is_superuser = False
        
        user.is_active = is_active
        if is_staff:
            user.is_staff = is_staff
        
        user.save()
        
        messages.success(request, f'Permissions updated for {user.email}')
        return redirect('user_management')
    
    return render(request, 'accounts/edit_user_permissions.html', {'edit_user': user})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

def is_admin(user):
    return user.is_authenticated and (
        user.user_type == 'admin' or user.user_type == 'superuser'
    )

@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    context = {
        'total_users': User.objects.count(),
        'customers': User.objects.filter(user_type='customer').count(),
        'admins': User.objects.filter(user_type='admin').count(),
        'superusers': User.objects.filter(user_type='superuser').count(),
        'recent_users': User.objects.order_by('-date_joined')[:10],
    }
    return render(request, 'accounts/dashboard.html', context)