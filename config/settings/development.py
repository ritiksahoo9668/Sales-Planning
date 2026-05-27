"""Development settings."""
from .base import *  # noqa: F401, F403

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Show every HTTP request in the terminal (fixes missing logs on Windows autoreloader).
MIDDLEWARE = list(MIDDLEWARE) + [  # noqa: F405
    'apps.common.middleware.RequestLoggingMiddleware',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'erp.requests': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

if DEBUG:
    try:
        import debug_toolbar  # noqa: F401
    except ImportError:
        pass
