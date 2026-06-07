from rest_framework.authentication import TokenAuthentication

COOKIE_NAME = 'auth_token'


class CookieTokenAuthentication(TokenAuthentication):
    """
    Lee el token desde la cookie HttpOnly en vez del header Authorization.
    Permite que SvelteKit SSR envíe requests autenticados sin exponer el token en JS.
    """
    def authenticate(self, request):
        token_key = request.COOKIES.get(COOKIE_NAME)
        if not token_key:
            return None
        return self.authenticate_credentials(token_key)