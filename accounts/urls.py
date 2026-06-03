from django.urls import path
from . import views

urlpatterns = [
    # Signup URLs
    path('signup/customer/', views.customer_signup_view, name='customer_signup'),
    path('signup/admin/', views.admin_signup_view, name='admin_signup'),
    path('signup/superuser/', views.superuser_signup_view, name='superuser_signup'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/<str:otp_type>/', views.verify_otp_view, name='verify_otp'),
    path('captcha/', views.generate_captcha, name='captcha'),
    
    # Password Management URLs
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('change-password/request/', views.change_password_request_view, name='change_password_request'),
    path('change-password/', views.change_password_with_otp_view, name='change_password_with_otp'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Address URLs
    path('addresses/', views.address_list_view, name='address_list'),
    path('addresses/add/', views.add_address_view, name='add_address'),
    path('addresses/<int:pk>/edit/', views.edit_address_view, name='edit_address'),
    path('addresses/<int:pk>/delete/', views.delete_address_view, name='delete_address'),
    path('addresses/<int:pk>/default/', views.set_default_address_view, name='set_default_address'),
    
    # Admin/Superuser Management URLs
    path('users/manage/', views.user_management_view, name='user_management'),
    path('users/<int:user_id>/permissions/', views.edit_user_permissions_view, name='edit_user_permissions'),
]