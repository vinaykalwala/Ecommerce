from django.urls import path

from . import views

urlpatterns = [

    path(
        "dashboard/",
        views.analytics_dashboard_view,
        name="analytics_dashboard"
    )
]