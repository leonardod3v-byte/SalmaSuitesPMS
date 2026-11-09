import re
from rest_framework import serializers


# ─── Teléfono ────────────────────────────────────────────────────────────────

def validar_telefono(value, requerido=False):
    """
    Permite números, espacios, guiones, paréntesis y el signo +.
    Debe tener al menos 7 dígitos.
    """
    if not value:
        if requerido:
            raise serializers.ValidationError("El teléfono es obligatorio.")
        return value

    value = value.strip()

    # Solo caracteres permitidos
    if not re.match(r'^[\+]?[\d\s\-\(\)]{7,20}$', value):
        raise serializers.ValidationError(
            "El teléfono solo puede contener números, espacios, guiones, paréntesis y el signo +."
        )

    # Al menos 7 dígitos (ignorando los símbolos)
    digitos = re.sub(r'\D', '', value)
    if len(digitos) < 7:
        raise serializers.ValidationError("El teléfono debe tener al menos 7 dígitos.")

    return value


# ─── Email ───────────────────────────────────────────────────────────────────

def validar_email(value, requerido=False):
    """
    Normaliza a minúsculas y valida el formato del correo.
    """
    if not value:
        if requerido:
            raise serializers.ValidationError("El correo electrónico es obligatorio.")
        return value

    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError as DjangoValidationError

    value = value.strip().lower()

    try:
        validate_email(value)
    except DjangoValidationError:
        raise serializers.ValidationError("Ingresa un correo electrónico válido.")

    return value


# ─── RIF (empresas) ──────────────────────────────────────────────────────────

def validar_rif(value):
    """
    Formato obligatorio: J-12345678-9 (letra, guion, 8 dígitos, guion, 1 dígito).
    """
    if not value:
        raise serializers.ValidationError("El RIF es obligatorio.")

    value = value.strip().upper()

    if not re.match(r'^[VEJPG]-\d{8}-\d$', value):
        raise serializers.ValidationError("El formato del RIF debe ser J-12345678-9.")

    return value


# ─── Nombres (personas o empresas) ───────────────────────────────────────────

def validar_nombre(value, requerido=True, campo="nombre"):
    """
    Solo letras, espacios, tildes y guiones.
    No permite solo números ni caracteres especiales raros.
    """
    if not value:
        if requerido:
            raise serializers.ValidationError(f"El {campo} es obligatorio.")
        return value

    value = value.strip()

    if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s\-\.\,\'&]+$', value):
        raise serializers.ValidationError(
            f"El {campo} solo puede contener letras, espacios, tildes, guiones y puntos."
        )

    if len(value) < 2:
        raise serializers.ValidationError(f"El {campo} debe tener al menos 2 caracteres.")

    return value


# ─── Número de documento de identidad ────────────────────────────────────────

def validar_numero_documento(value, tipo):
    """
    Valida según el tipo:
    - V, E: 6 a 9 dígitos
    - J: 8 a 10 dígitos
    - P: alfanumérico de 6 a 15 caracteres
    """
    if not value:
        raise serializers.ValidationError("El número de documento es obligatorio.")

    value = value.strip()

    if tipo in ['V', 'E']:
        if not re.match(r'^\d{6,9}$', value):
            raise serializers.ValidationError(
                f"Para {tipo}, el documento debe tener entre 6 y 9 dígitos (sin letras ni símbolos)."
            )
    elif tipo == 'J':
        if not re.match(r'^\d{8,10}$', value):
            raise serializers.ValidationError(
                "Para J, el documento debe tener entre 8 y 10 dígitos."
            )
    elif tipo == 'P':
        if not re.match(r'^[A-Za-z0-9]{6,15}$', value):
            raise serializers.ValidationError(
                "Para P, el documento debe ser alfanumérico de 6 a 15 caracteres."
            )
    else:
        raise serializers.ValidationError("Tipo de documento no válido.")

    return value.upper() if tipo == 'P' else value


# ─── Username (usuarios) ─────────────────────────────────────────────────────

def validar_username(value):
    """
    Alfanumérico + guion bajo + guion medio. Sin espacios.
    Entre 3 y 30 caracteres.
    """
    if not value:
        raise serializers.ValidationError("El nombre de usuario es obligatorio.")

    value = value.strip()

    if not re.match(r'^[A-Za-z0-9_\-]{3,30}$', value):
        raise serializers.ValidationError(
            "El usuario debe tener entre 3 y 30 caracteres. Solo letras, números, guion y guion bajo (sin espacios)."
        )

    return value


# ─── Dirección ───────────────────────────────────────────────────────────────

def validar_direccion(value, requerido=True):
    """
    Solo valida que no esté vacía. La dirección puede tener cualquier combinación.
    """
    if not value:
        if requerido:
            raise serializers.ValidationError("La dirección es obligatoria.")
        return value

    value = value.strip()

    if len(value) < 5:
        raise serializers.ValidationError("La dirección debe tener al menos 5 caracteres.")

    return value
