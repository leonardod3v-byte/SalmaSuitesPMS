from rest_framework.authentication import TokenAuthentication

COOKIE_NAME = 'auth_token'

class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token_key = request.COOKIES.get(COOKIE_NAME)
        if not token_key:
            return None
        return self.authenticate_credentials(token_key)