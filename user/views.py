from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login
import requests
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer


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
    client_id = "your-client-id.apps.googleusercontent.com"
    client_secret = "your-client-secret"
    code = request.GET.get("code")
    url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "your-backend-redirect-uri",
        "grant_type": "authorization_code",
    }
    r = requests.post(url, data=data)
    token_data = r.json()

    access_token = token_data.get("access_token")
    # Fetch user details from Google's userinfo endpoint
    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    print(user_info)

    User = get_user_model()
    # Try to retrieve the user by their email
    try:
        user = User.objects.get(email=user_info['email'])
    except User.DoesNotExist:
        # Create a new user if does not exist
        user = User.objects.create(
            username=user_info['email'],
            email=user_info['email'],
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', '')
        )
        user.set_unusable_password()  # Important if password login isn't meant to be used
        user.save()

    # Authenticate session
    login(request, user)

    # Create a token for your DRF TokenAuthentication
    token, created = Token.objects.get_or_create(user=user)
    return redirect(f"http://localhost:5173/?token={token.key}")