from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .cookies import clear_refresh_cookie, get_refresh_cookie, set_refresh_cookie
from .serializers import ChangePasswordSerializer, LoginSerializer, RegisterSerializer, UserSerializer


def _session_response(user, tokens, *, status_code=status.HTTP_200_OK):
    """Access token + user in the body, refresh token in the httpOnly cookie."""
    response = Response({"access": tokens.access, "user": UserSerializer(user).data}, status=status_code)
    set_refresh_cookie(response, tokens.refresh)
    return response


class PublicAuthView(APIView):
    """
    Base for endpoints that work without an access token (they rely on the
    password or on the refresh cookie instead).

    `get_authenticate_header` makes DRF answer 401 (not 403) when credentials
    are wrong, which is what the frontend's interceptor expects.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    def get_authenticate_header(self, request):
        return 'Bearer realm="api"'


class RegisterView(PublicAuthView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.register_user(**serializer.validated_data)
        return _session_response(user, services.issue_tokens(user), status_code=status.HTTP_201_CREATED)


class LoginView(PublicAuthView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.login(request=request, **serializer.validated_data)
        return _session_response(user, services.issue_tokens(user))


class RefreshView(PublicAuthView):
    throttle_scope = "auth_refresh"

    def post(self, request):
        try:
            tokens = services.rotate_refresh_token(get_refresh_cookie(request))
        except services.SessionExpired as exc:
            response = Response(
                {"error": {"code": exc.detail.code, "message": str(exc.detail)}},
                status=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": self.get_authenticate_header(request)},
            )
            clear_refresh_cookie(response)  # a dead cookie is useless; drop it
            return response
        response = Response({"access": tokens.access})
        set_refresh_cookie(response, tokens.refresh)
        return response


class LogoutView(PublicAuthView):
    throttle_scope = "auth_refresh"

    def post(self, request):
        services.logout(get_refresh_cookie(request))
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        tokens = services.change_password(user=request.user, new_password=serializer.validated_data["new_password"])
        return _session_response(request.user, tokens)
