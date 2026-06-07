from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.utils.crypto import get_random_string
import uuid

User = get_user_model()
RESET_CACHE_PREFIX = "pwd_reset_"

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """
    Controlador central de login seguro.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Credenciales incompletas.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Usuario o contraseña incorrectos.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'error': 'Esta cuenta está desactivada.'}, status=status.HTTP_403_FORBIDDEN)

    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'nombre': user.first_name,
            'apellido': user.last_name,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def logout_view(request):
    """
    Invalida el token de sesión actual de DRF.
    """
    request.user.auth_token.delete()
    return Response({'message': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def request_password_reset(request):
    """
    Paso 1: Genera y despacha el token de verificación de 6 dígitos.
    """
    email = request.data.get('email')
    if not email:
        return Response({'error': 'El correo electrónico es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Ofuscación de seguridad: No revelar si el correo existe o no en la BD
        return Response({'message': 'Si el correo está registrado, se enviará un código de verificación.'}, status=status.HTTP_200_OK)

    code = get_random_string(6, allowed_chars='0123456789')
    
    # Caché atómica por 15 minutos
    cache.set(f'{RESET_CACHE_PREFIX}{email}', {'user_id': user.id, 'code': code}, timeout=900)
    
    # Aquí se dispararía el servicio de notificaciones asíncrono
    print(f"[EMAIL SIMULATION] Código para {email}: {code}")

    return Response({'message': 'Si el correo está registrado, se enviará un código de verificación.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def verify_reset_code(request):
    """
    Paso 2: Compara el código ingresado e intercambia por un JWT efímero.
    """
    email = request.data.get('email')
    code = request.data.get('code')

    if not email or not code:
        return Response({'error': 'Datos incompletos.'}, status=status.HTTP_400_BAD_REQUEST)

    stored = cache.get(f'{RESET_CACHE_PREFIX}{email}')
    if not stored or stored['code'] != code:
        return Response({'error': 'Código inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)

    # Generar token único de un solo uso para autorizar el cambio definitivo
    verified_token = str(uuid.uuid4())
    stored['verified_token'] = verified_token
    cache.set(f'{RESET_CACHE_PREFIX}{email}', stored, timeout=300) # 5 minutos para escribir la contraseña

    return Response({
        'message': 'Código verificado con éxito.',
        'token': verified_token
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reset_password(request):
    """
    Paso 3: Realiza la mutación de la contraseña de manera persistente.
    """
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
        
        # Exterminar tokens antiguos para forzar re-autenticación en todos los dispositivos
        Token.objects.filter(user=user).delete()
        cache.delete(f'{RESET_CACHE_PREFIX}{email}')
        
        return Response({'message': 'Contraseña actualizada correctamente.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def profile_view(request):
    """
    Retorna los datos del perfil del usuario actualmente autenticado.
    """
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'nombre': user.first_name,
        'apellido': user.last_name,
    }, status=status.HTTP_200_OK)