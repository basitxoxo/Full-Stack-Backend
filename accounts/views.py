from rest_framework import generics, permissions
from .serializers import ProfileSerializer, RegisterSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import LoginSerializer
from django.conf import settings
from .models import Profile
from .permissions import IsOwner
from .serializers import ChangePasswordSerializer

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .permissions import IsAdmin
from .throttles import (
    LoginRateThrottle,
    RegisterRateThrottle,
    RefreshRateThrottle,
)
from django.contrib.auth import get_user_model

from .serializers import AdminChangePasswordSerializer

User = get_user_model()

ADMIN_LOGIN_START = 9
ADMIN_LOGIN_END = 17

class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "Welcome Admin"})
    
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        
        current_hour = timezone.localtime(timezone.now()).hour

        if user.groups.filter(name="Admin").exists():
            if not (ADMIN_LOGIN_START <= current_hour < ADMIN_LOGIN_END):
                return Response(
                        {
                            "detail": "Admin login is only allowed between 9:00 AM and 5:00 PM."
                        },
                status=status.HTTP_403_FORBIDDEN,
            )
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        role = user.groups.first().name if user.groups.exists() else "User"
        response = Response(
            {
                "access": str(access),
                "username": user.username,
                "role": role,
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
    key=settings.REFRESH_TOKEN_COOKIE_NAME,
    value=str(refresh),
    httponly=settings.REFRESH_TOKEN_COOKIE_HTTPONLY,
    secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
    samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
    max_age=settings.REFRESH_TOKEN_COOKIE_MAX_AGE,
) 
        return response



@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFCookieView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set."})

class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    throttle_classes = [RefreshRateThrottle]
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        response = Response(
            {
                "access": serializer.validated_data["access"],
            }
        )

        if "refresh" in serializer.validated_data:
            response.set_cookie(
    key=settings.REFRESH_TOKEN_COOKIE_NAME,
    value=serializer.validated_data["refresh"],
    httponly=settings.REFRESH_TOKEN_COOKIE_HTTPONLY,
    secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
    samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
    max_age=settings.REFRESH_TOKEN_COOKIE_MAX_AGE,
)

        return response
    
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(
    key=settings.REFRESH_TOKEN_COOKIE_NAME,
    secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
    samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
)

        return response
        

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        profile = Profile.objects.get(user=self.request.user)

        self.check_object_permissions(self.request, profile)

        return profile

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        request.user.set_password(
            serializer.validated_data["new_password"]
        )
        request.user.save()

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )
    

class AdminChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = AdminChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(
            username=serializer.validated_data["username"]
        )

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save()

        return Response(
            {
                "detail": f"Password for '{user.username}' changed successfully."
            },
            status=status.HTTP_200_OK,
        )