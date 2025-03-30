from manga.helpers import update_manga_history
from manga.models import UserHistory
from manga.serializers import UserHistorySerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
# from django_ratelimit.decorators import ratelimit


import requests
# from django.conf import settings
from allauth.socialaccount.models import SocialApp
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import (
    GoogleOAuth2Adapter)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

# redirect to this url on Google icon click
# https://accounts.google.com/o/oauth2/auth?client_id=369026344558-458lvpvju2frq5uv2sopk3qqnut9odbl.apps.googleusercontent.com&redirect_uri=http://localhost:8000/users/google/callback/&response_type=code&scope=email%20profile&access_type=offline&prompt=consent


class GoogleOAuthCallbackView(APIView):
    """
    Handles Google OAuth2 callback and exchanges the code for an access token.
    """

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response(
                {"error": "Authorization code not found"}, status=400)

        # Get client_id and client_secret from Django admin
        try:
            google_app = SocialApp.objects.get(provider="google")
            client_id = google_app.client_id
            client_secret = google_app.secret
        except SocialApp.DoesNotExist:
            return Response(
                {"error": "Google OAuth app not configured"}, status=500)

        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": (
                "http://localhost:8000/users/google/callback/"),
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()

        if "access_token" not in token_data:
            return Response({
                "error": "Failed to obtain access token",
                "details": token_data
            }, status=400)

        return Response({
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token")
        })


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LoginView(APIView):
    # @ratelimit(key='ip', rate='5/m', method='POST', block=True)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                serializer.validated_data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data)


class AddReadHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        manga_id = request.data.get("manga_id")
        request.user.add_to_history(manga_id)
        return Response(
            {"message": "History updated"},
            status=status.HTTP_200_OK
        )


class UserHistoryViewSet(viewsets.ModelViewSet):
    """Handles retrieving and updating manga reading history."""

    serializer_class = UserHistorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return UserHistory.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Update manga reading history when a user reads a chapter."""
        user = request.user
        manga_id = request.data.get("manga_id")
        chapter = request.data.get("chapter")

        history = update_manga_history(user, manga_id, chapter)
        return Response(UserHistorySerializer(history).data)
