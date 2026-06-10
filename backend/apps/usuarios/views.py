from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
import uuid

from .serializers import (
    UserSerializer,
    UserCreateUpdateSerializer,
    LoginSerializer,
    CambioPasswordSerializer
)
from . import services
from apps.bitacora.models import ActividadLog
from apps.bitacora.serializers import ActividadLogSerializer

User = get_user_model()
RESET_CACHE_PREFIX = "pwd_reset_"

# Autenticación --------------------------------------------------

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
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'nombre_completo': user.nombre_completo,
        }
    }, status=status.HTTP_200_OK)

    # Establecer cookie HttpOnly con el token
    response.set_cookie(
        key='auth_token',
        value=token.key,
        httponly=True,
        secure=False,  # True en producción con HTTPS
        samesite='Lax',
        max_age=60 * 60 * 24 * 7  # 7 días
    )
    return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def logout_view(request):
    request.user.auth_token.delete()
    return Response({'message': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)

# Perfil --------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_password_view(request):
    serializer = CambioPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    try:
        services.cambiar_password(
            user,
            serializer.validated_data['old_password'],
            serializer.validated_data['new_password']
        )
        return Response({'message': 'Contraseña actualizada correctamente.'})
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Recuperación de contraseña ------------------------------------

from django.core.mail import send_mail
from django.conf import settings

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def request_password_reset(request):
    """
    Paso 1: Genera un código de 6 dígitos y lo envía por correo electrónico.
    """
    email = request.data.get('email')
    if not email:
        return Response({'error': 'El correo electrónico es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # No revelar si el correo existe o no
        return Response({'message': 'Si el correo está registrado, recibirás un código de verificación.'}, status=status.HTTP_200_OK)

    # Generar código numérico de 6 dígitos
    code = get_random_string(6, allowed_chars='0123456789')

    # Guardar en caché por 15 minutos
    cache.set(f'{RESET_CACHE_PREFIX}{email}', {'user_id': user.id, 'code': code}, timeout=900)

    # Enviar correo real
    try:
        send_mail(
            subject='Código de recuperación - Salma Suite VIP',
            message=f'Tu código de verificación es: {code}\n\nEste código expira en 15 minutos.\n\nSi no solicitaste este cambio, ignora este mensaje.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        # Si falla el envío, eliminar el código de caché y devolver error
        cache.delete(f'{RESET_CACHE_PREFIX}{email}')
        return Response({'error': 'Error al enviar el correo. Intenta de nuevo más tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Si el correo está registrado, recibirás un código de verificación.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def verify_reset_code(request):
    email = request.data.get('email')
    code = request.data.get('code')
    if not email or not code:
        return Response({'error': 'Datos incompletos.'}, status=status.HTTP_400_BAD_REQUEST)
    stored = cache.get(f'{RESET_CACHE_PREFIX}{email}')
    if not stored or stored['code'] != code:
        return Response({'error': 'Código inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)
    verified_token = str(uuid.uuid4())
    stored['verified_token'] = verified_token
    cache.set(f'{RESET_CACHE_PREFIX}{email}', stored, timeout=300)
    return Response({'message': 'Código verificado con éxito.', 'token': verified_token}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')
    token = request.data.get('token')
    if not email or not new_password or not token:
        return Response({'error': 'Datos incompletos.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(new_password) < 8:
        return Response({'error': 'La contraseña debe tener al menos 8 caracteres.'}, status=status.HTTP_400_BAD_REQUEST)
    stored = cache.get(f'{RESET_CACHE_PREFIX}{email}')
    if not stored or 'verified_token' not in stored or stored['verified_token'] != token:
        return Response({'error': 'La sesión de recuperación es inválida o expiró.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=stored['user_id'])
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        cache.delete(f'{RESET_CACHE_PREFIX}{email}')
        return Response({'message': 'Contraseña actualizada correctamente.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

# Gestión de usuarios (admin) -----------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def gestion_usuarios(request):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        usuarios = services.listar_usuarios()
        serializer = UserSerializer(usuarios, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def gestion_usuario_individual(request, pk):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        if user == request.user and 'role' in request.data and request.data['role'] != 'admin':
            if User.objects.filter(role='admin', is_active=True).count() <= 1:
                return Response({'error': 'No puedes quitarte el rol de administrador siendo el único administrador.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserCreateUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if user == request.user:
            return Response({'error': 'No puedes desactivar tu propio usuario.'}, status=status.HTTP_400_BAD_REQUEST)
        services.desactivar_usuario(user)
        return Response({'message': 'Usuario desactivado.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def actividad_usuario(request, pk):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    actividades = ActividadLog.objects.filter(id_usuario=user).order_by('-fecha_hora')[:50]
    serializer = ActividadLogSerializer(actividades, many=True)
    return Response(serializer.data)