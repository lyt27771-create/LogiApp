"""Entorno de desarrollo: se usa en el laboratorio y en cada máquina local."""

from .base import *  # noqa: F401,F403

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
