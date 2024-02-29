"""
rest_conf.py
"""
from horilla import settings
from horilla.settings import INSTALLED_APPS


# Injecting installed apps to settings

REST_APPS = ["rest_framework",
             "rest_framework_simplejwt",
             "auth_api",
             "attendance_api",
             "leave_api",
             "employee_api",
             "base_api"]

INSTALLED_APPS.extend(REST_APPS)

REST_FRAMEWORK_SETTINGS = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'PAGE_SIZE': 50,
}
# Inject the REST framework settings into the Django project settings
setattr(settings, 'REST_FRAMEWORK', REST_FRAMEWORK_SETTINGS)
