from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer
from google.oauth2 import id_token
from google.auth.transport import requests


class Signup(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    http_method_names = ["post"]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.validated_data)
        token = Token.objects.create(user=user)

        # Serialize the user object
        user_serializer = UserSerializer(token.user)
        serialized_user = user_serializer.data

        return Response({"token": token.key, "user": serialized_user})


class Signin(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(Signin, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])

        # Serialize the user object
        user_serializer = UserSerializer(token.user)
        serialized_user = user_serializer.data

        return Response({"token": token.key, "user": serialized_user})


@api_view(['POST'])
@permission_classes([AllowAny])
def google_complete(request):
    client_id = "536694079392-l8fshhc5500re28bk2dk82i9k14h14l6.apps.googleusercontent.com"
    # client_secret = "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"

    token = request.data.get("token")
    
    if not token:
        print("Token is missing")
        return Response({"error": "Token is missing"}, status=400)

    # Validate the token and get user info
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        
        # idinfo['sub'] is user's Google ID
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        
        User = get_user_model()
        # Try to retrieve the user by their email
        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': first_name, 'last_name': last_name}
        )
        
        if created:
            user.set_unusable_password()  # Important if password login isn't meant to be used
            user.save()

        # Authenticate session
        login(request, user)

        # Create a token for your DRF TokenAuthentication
        token, created = Token.objects.get_or_create(user=user)
        return redirect(f"http://localhost:5173/?token={token.key}")
        
    except ValueError:
        # Invalid token
        print("Invalid token")
        return Response({"error": "Invalid token"}, status=400)