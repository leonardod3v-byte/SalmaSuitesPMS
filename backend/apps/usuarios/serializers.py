from rest_framework import serializers
from .models import User
from apps.utils import (
    validar_email, validar_telefono, validar_nombre,
    validar_username,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'nombre_completo', 'is_active', 'last_login']
        read_only_fields = ['id', 'last_login']


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    phone = serializers.CharField(required=False, allow_blank=True)
    nombre_completo = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'nombre_completo', 'password', 'is_active']
        read_only_fields = ['id']

    def validate_username(self, value):
        return validar_username(value)

    def validate_email(self, value):
        return validar_email(value)

    def validate_phone(self, value):
        return validar_telefono(value)

    def validate_nombre_completo(self, value):
        return validar_nombre(value, campo="nombre completo")

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user_obj = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuario o contraseña incorrectos.')

        if not user_obj.is_active:
            raise serializers.ValidationError('Tu cuenta ha sido desactivada. Contacta al administrador.')

        user = authenticate(**data)
        if user:
            return user

        raise serializers.ValidationError('Usuario o contraseña incorrectos.')


class CambioPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Las contraseñas no coinciden.'})
        return data
