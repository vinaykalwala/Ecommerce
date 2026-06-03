from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameOrMobileBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with:
    - Email
    - Username
    - Mobile Number
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None
        
        try:
            # Try to find user by email, username, or mobile number
            user = User.objects.get(
                Q(email=username) | 
                Q(username=username) | 
                Q(mobile_number=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing attacks
            User().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None