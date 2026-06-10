from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

def crear_usuario(username: str, password: str, **kwargs) -> User:
    if User.objects.filter(username=username).exists():
        raise ValidationError('El nombre de usuario ya existe.')
    user = User(username=username, **kwargs)
    if password:
        user.set_password(password)
    user.save()
    return user

def editar_usuario(user: User, data: dict) -> User:
    if 'username' in data:
        del data['username']  # no se permite cambiar username
    for campo, valor in data.items():
        if campo == 'password':
            user.set_password(valor)
        elif campo not in ['id', 'last_login']:
            setattr(user, campo, valor)
    user.save()
    return user

def desactivar_usuario(user: User) -> User:
    user.is_active = False
    user.save()
    return user

def listar_usuarios() -> list:
    return User.objects.all()

def cambiar_password(user: User, old_password: str, new_password: str):
    if not user.check_password(old_password):
        raise ValidationError('La contraseña actual es incorrecta.')
    user.set_password(new_password)
    user.save()