from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = [
        ('admin', 'Administrador'),
        ('recepcionista', 'Recepcionista'),
    ]

    role = models.CharField(max_length=20, choices=ROLES, default='recepcionista')
    phone = models.CharField(max_length=20, blank=True)
    nombre_completo = models.CharField(max_length=150, blank=True)

    # Eliminamos first_name y last_name
    first_name = None
    last_name = None

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_recepcionista(self):
        return self.role == 'recepcionista'
