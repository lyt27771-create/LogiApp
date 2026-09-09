from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Datos del WMS", {"fields": ("cedula", "telefono", "rol")}),
    )
    list_display = UserAdmin.list_display + ("rol",)
    list_filter = UserAdmin.list_filter + ("rol",)