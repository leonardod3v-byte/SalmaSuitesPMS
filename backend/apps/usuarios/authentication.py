from rest_framework.authentication import TokenAuthentication

COOKIE_NAME = 'auth_token'

class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token_key = request.COOKIES.get(COOKIE_NAME)
        if token_key:
            try:
                return self.authenticate_credentials(token_key)
            except Exception:
                pass
        # Fallback al header Authorization
        return super().authenticate(request)