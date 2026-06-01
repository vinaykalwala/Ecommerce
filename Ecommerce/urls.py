from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from accounts import views
from django.contrib.auth import views as auth_views
from catalog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "",
        views.home_view,
        name="home"
    ),

    path("accounts/",include("accounts.urls")),
    path("accounts/login/",auth_views.LoginView.as_view(template_name="accounts/login.html"),name="login"),
    path("catalog/",include("catalog.urls")),
    path("cart/",include("cart.urls")),
    path("wishlist/",include("wishlist.urls")),
    path("coupons/",include("coupons.urls")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)