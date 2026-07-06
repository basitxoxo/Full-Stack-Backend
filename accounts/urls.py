from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    CookieTokenRefreshView,
    LogoutView,
    ProfileDetailView,
    AdminOnlyView,
    ChangePasswordView,
    CSRFCookieView,
    AdminChangePasswordView,
) 

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("csrf/", CSRFCookieView.as_view(), name="csrf"),
    path("admin-only/", AdminOnlyView.as_view(), name="admin-only"),
    path("profile/", ProfileDetailView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "admin/change-password/",
        AdminChangePasswordView.as_view(),
        name="admin-change-password",
    ),
]
