from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)
        self.jwt_authentication = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        await self.authenticate_user(scope)
        return await super().__call__(scope, receive, send)

    @sync_to_async
    def authenticate_user(self, scope):
        try:
            headers = dict(scope["headers"])
            if b"authorization" in headers:

                token_name, token_key = headers[b"authorization"].decode().split()

                if token_name == "Bearer":
                    validated_token = self.jwt_authentication.get_validated_token(raw_token=token_key)
                    validated_user = self.jwt_authentication.get_user(validated_token)
                    scope["user"] = validated_user

                else:
                    scope["user"] = None
            else:
                scope["user"] = None
        except (InvalidToken, KeyError):
            scope["user"] = None
