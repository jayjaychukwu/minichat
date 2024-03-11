from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)
        self.jwt_authentication = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        try:
            auth = scope["headers"]["authorization"].decode().split()[1]
            validated_token = self.jwt_authentication.get_validated_token(auth)
            scope["user"] = validated_token.user
        except (InvalidToken, KeyError):
            scope["user"] = None

        return await self.inner(scope, receive, send)
