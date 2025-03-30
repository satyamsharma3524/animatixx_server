from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    GoogleLogin,
    GoogleOAuthCallbackView,
    RegisterView,
    LoginView,
    UserView,
    AddReadHistoryView
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserView.as_view(), name='user'),
    path('history/', AddReadHistoryView.as_view(), name='add_history'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('google/callback/',
         GoogleOAuthCallbackView.as_view(), name='google_callback'),
]
