"""Entorno de servidor. No se ha probado en un despliegue real todavía:
son los mínimos de seguridad recomendados por Django para DEBUG=False."""

from .base import *  # noqa: F401,F403

DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
