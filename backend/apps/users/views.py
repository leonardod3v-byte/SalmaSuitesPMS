from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .serializers import LoginSerializer, UserSerializer
import random

User = get_user_model()

RESET_CACHE_PREFIX = 'pwd_reset:'
RESET_TTL = 60 * 15  # 15 minutos en segundos

COOKIE_NAME = 'auth_token'
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 días


# ── Login / Logout / Perfil ────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data
    token, _ = Token.objects.get_or_create(user=user)

    response = Response({
        'user': UserSerializer(user).data,
        'message': 'Login exitoso',
    })
    response.set_cookie(
        key=COOKIE_NAME,
        value=token.key,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        path='/',
    )
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def logout_view(request):
    token_key = request.COOKIES.get(COOKIE_NAME)
    if token_key:
        Token.objects.filter(key=token_key).delete()

    response = Response({'message': 'Logout exitoso'})
    response.delete_cookie(key=COOKIE_NAME, path='/', samesite='Lax')
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def profile_view(request):
    return Response(UserSerializer(request.user).data)


# ── Recuperación de contraseña ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def request_password_reset(request):
    email = request.data.get('email', '').strip().lower()

    if not email:
        return Response({'error': 'El email es requerido.'}, status=400)

    if '@' not in email or '.' not in email.split('@')[-1]:
        return Response({'error': 'El formato del email no es válido.'}, status=400)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'No existe ninguna cuenta registrada con ese correo.'},
            status=404,
        )

    if not user.is_active:
        return Response(
            {'error': 'Esta cuenta está desactivada. Contacta al administrador.'},
            status=403,
        )

    code = ''.join(random.choices('0123456789', k=6))

    # Guardar en caché en vez del dict en memoria
    # Si Django reinicia, el código expira correctamente (TTL = 15 min)
    cache.set(
        f'{RESET_CACHE_PREFIX}{email}',
        {'code': code, 'user_id': user.id},
        timeout=RESET_TTL,
    )

    try:
        send_mail(
            subject='🔐 Código de recuperación - Salma Suite VIP',
            message=(
                f'Hola {user.username},\n\n'
                f'Tu código de recuperación es: {code}\n\n'
                f'Válido por 15 minutos.\n'
                f'Si no solicitaste esto, ignora este mensaje.\n\n'
                f'Salma Suite VIP - Sistema de Gestión Hotelera'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': f'Código enviado a {email}', 'email': email})

    except Exception as e:
        cache.delete(f'{RESET_CACHE_PREFIX}{email}')
        return Response({'error': f'Error al enviar el email: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def verify_reset_code(request):
    email = request.data.get('email', '').strip().lower()
    code  = request.data.get('code', '').strip()

    if not email or not code:
        return Response({'error': 'Email y código son requeridos.'}, status=400)

    stored = cache.get(f'{RESET_CACHE_PREFIX}{email}')

    if not stored:
        # Cache miss = nunca se solicitó, o el TTL de 15 min ya expiró
        return Response(
            {'error': 'El código ha expirado o no existe. Solicita uno nuevo.'},
            status=400,
        )

    if stored['code'] != code:
        return Response({'error': 'El código ingresado es incorrecto.'}, status=400)

    try:
        user = User.objects.get(id=stored['user_id'])
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=404)

    # Generar token JWT de corta duración (15 min, según SIMPLE_JWT en settings)
    # Solo se usa para autorizar el siguiente paso (reset_password)
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access  = str(refresh.access_token)

    # Marcar en caché que el código fue verificado, guardando el access token
    # para validarlo en reset_password. Mismo TTL de 15 min.
    cache.set(
        f'{RESET_CACHE_PREFIX}{email}',
        {'code': code, 'user_id': user.id, 'verified_token': access},
        timeout=RESET_TTL,
    )

    return Response({'valid': True, 'access': access})
    # ⚠️ No devolvemos el refresh token — no tiene sentido para un reset de contraseña


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reset_password(request):
    email        = request.data.get('email', '').strip().lower()
    new_password = request.data.get('new_password', '')
    token        = request.data.get('token', '')          # access JWT del paso anterior

    if not email or not new_password or not token:
        return Response({'error': 'Datos incompletos.'}, status=400)

    if len(new_password) < 8:
        return Response(
            {'error': 'La contraseña debe tener al menos 8 caracteres.'},
            status=400,
        )

    stored = cache.get(f'{RESET_CACHE_PREFIX}{email}')
    if not stored or 'verified_token' not in stored:
        return Response(
            {'error': 'La sesión de recuperación es inválida o ya expiró.'},
            status=400,
        )

    # Validar que el token recibido coincide con el que emitimos nosotros
    # Esto impide que alguien salte verify_reset_code y llame reset_password directamente
    if stored['verified_token'] != token:
        return Response({'error': 'Token de recuperación inválido.'}, status=400)

    try:
        user = User.objects.get(id=stored['user_id'])
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=404)

    user.set_password(new_password)
    user.save()

    # Invalidar todos los tokens DRF existentes del usuario para forzar re-login
    Token.objects.filter(user=user).delete()

    # Limpiar el registro de recuperación de la caché
    cache.delete(f'{RESET_CACHE_PREFIX}{email}')

    return Response({'message': 'Contraseña actualizada correctamente.'})