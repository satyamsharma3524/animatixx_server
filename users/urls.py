from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from .views import (
    GoogleLogin,
    GoogleOAuthCallbackView,
    RegisterView,
    LoginView,
    UserHistoryViewSet,
    UserView,
    AddReadHistoryView
)


router = DefaultRouter()
router.register(r'user-history', UserHistoryViewSet, basename="user-history")


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserView.as_view(), name='user'),
    path('history/', AddReadHistoryView.as_view(), name='add_history'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('google/callback/',
         GoogleOAuthCallbackView.as_view(), name='google_callback'),
    path('', include(router.urls)),
]
