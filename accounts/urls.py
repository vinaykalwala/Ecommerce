from django.urls import path

from . import views

urlpatterns = [

    path(
        "signup/",
        views.signup_view,
        name="signup"
    ),

    path(
        "profile/",
        views.profile_view,
        name="profile"
    ),

    path(
        "profile/edit/",
        views.edit_profile_view,
        name="edit_profile"
    ),

    path(
        "addresses/",
        views.address_list_view,
        name="address_list"
    ),

    path(
        "addresses/add/",
        views.add_address_view,
        name="add_address"
    ),

    path(
        "addresses/<int:pk>/edit/",
        views.edit_address_view,
        name="edit_address"
    ),

    path(
        "addresses/<int:pk>/delete/",
        views.delete_address_view,
        name="delete_address"
    ),

    path(
        "addresses/<int:pk>/default/",
        views.set_default_address_view,
        name="set_default_address"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
]