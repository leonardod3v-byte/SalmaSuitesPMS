from django.contrib.auth import get_user_model, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .serializers import LoginSerializer, UserSerializer
import random
from datetime import datetime, timedelta

User = get_user_model()
reset_codes = {}


def get_tokens_for_user(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login exitoso'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Logout exitoso'})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def profile_view(request):
    # Usar el serializer en lugar de construir el dict manualmente
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def request_password_reset(request):
    email = request.data.get('email', '').strip().lower()

    if not email:
        return Response({'error': 'El email es requerido.'}, status=400)

    # Validar formato básico de email
    if '@' not in email or '.' not in email.split('@')[-1]:
        return Response({'error': 'El formato del email no es válido.'}, status=400)

    # Verificar si existe en la BD
    # A diferencia de antes, aquí SÍ distinguimos si existe o no
    # para dar feedback real al usuario en el frontend
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'No existe ninguna cuenta registrada con ese correo.'},
            status=404
        )

    # Verificar que la cuenta esté activa
    if not user.is_active:
        return Response(
            {'error': 'Esta cuenta está desactivada. Contacta al administrador.'},
            status=403
        )

    # Generar código de 6 dígitos con expiración de 15 minutos
    code = ''.join(random.choices('0123456789', k=6))
    reset_codes[email] = {
        'code': code,
        'user_id': user.id,
        'expires': datetime.now() + timedelta(minutes=15)
    }

    try:
        send_mail(
            subject='🔐 Código de recuperación - Salma Suite VIP',
            message=f'''Hola {user.username},

Tu código de recuperación es: {code}

Válido por 15 minutos.
Si no solicitaste esto, ignora este mensaje.

Salma Suite VIP - Sistema de Gestión Hotelera''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({
            'message': f'Código enviado a {email}',
            'email': email
        })
    except Exception as e:
        # Si falla el envío limpiamos el código para no dejar datos huérfanos
        reset_codes.pop(email, None)
        return Response(
            {'error': f'Error al enviar el email: {str(e)}'},
            status=500
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def verify_reset_code(request):
    email = request.data.get('email', '').strip().lower()
    code = request.data.get('code', '').strip()

    if not email or not code:
        return Response({'error': 'Email y código son requeridos.'}, status=400)

    stored = reset_codes.get(email)

    if not stored:
        return Response(
            {'error': 'No hay ninguna solicitud activa para este correo.'},
            status=400
        )

    if datetime.now() > stored['expires']:
        reset_codes.pop(email, None)
        return Response(
            {'error': 'El código ha expirado. Solicita uno nuevo.'},
            status=400
        )

    if stored['code'] != code:
        return Response({'error': 'El código ingresado es incorrecto.'}, status=400)

    try:
        user = User.objects.get(id=stored['user_id'])
        tokens = get_tokens_for_user(user)
        return Response({
            'valid': True,
            'access': tokens['access'],
            'refresh': tokens['refresh']
        })
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reset_password(request):
    email = request.data.get('email', '').strip().lower()
    new_password = request.data.get('new_password', '')
    token = request.data.get('token', '')

    if not email or not new_password or not token:
        return Response({'error': 'Datos incompletos.'}, status=400)

    # Validar longitud mínima de contraseña
    if len(new_password) < 8:
        return Response(
            {'error': 'La contraseña debe tener al menos 8 caracteres.'},
            status=400
        )

    stored = reset_codes.get(email)
    if not stored:
        return Response(
            {'error': 'La sesión de recuperación es inválida o ya expiró.'},
            status=400
        )

    try:
        user = User.objects.get(id=stored['user_id'])
        user.set_password(new_password)
        user.save()

        # Limpiar código una vez usado
        reset_codes.pop(email, None)

        return Response({'message': 'Contraseña actualizada correctamente.'})

    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=404)