from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Autenticación por sesión de Django sin verificación CSRF.

    Permite que el frontend SvelteKit en localhost:5173 consuma
    la API en localhost:8000 sin necesidad de incluir el token
    CSRF en cada request, ya que ambos corren en orígenes distintos.

    En producción se debe migrar a JWT completo con
    rest_framework_simplejwt para mayor seguridad.
    """
    def enforce_csrf(self, request):
        return