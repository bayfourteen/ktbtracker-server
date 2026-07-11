from .base import BASE_DIR, DEBUG

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "()": "colorlog.ColoredFormatter",
            "format": "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            }
        },
        "verbose": {
            "format": "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s (%(filename)s:%(lineno)s)",
        },
        "call_trace": {
            "format": "[%(asctime)s] [%(levelname)-8s] %(message)s (%(pathname)s:%(lineno)s)",
        }
    },

    "handlers": {
        "console": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "DEBUG",
            "formatter": "verbose",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "debug.log",
        },
        "call_trace": {
            "level": "DEBUG",
            "formatter": "call_trace",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "trace.log",
        },
    },

    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
        "propagate": False,
    },

    "loggers": {
        "ktbtracker": {
            "level": "DEBUG",
            "formatter": "verbose",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "tracking": {
            "level": "DEBUG",
            "formatter": "verbose",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "call_trace": {
            "level": "DEBUG",
            "formatter": "call_trace",
            "handlers": ["file"],
            "propagate": False,
        },
        "django": {
            "level": "ERROR",
            "formatter": "verbose",
            "handlers": ["file"],
            "propagate": False,
        },
        "django.db": {
            "level": "DEBUG" if DEBUG else "ERROR",
            "formatter": "verbose",
            "handlers": ["file"],
            "propagate": False,
        },
        "django.auth": {
            "level": "DEBUG",
            "formatter": "verbose",
            "handlers": ["file"],
            "propagate": False,
        },
        "django.request": {
            "level": "DEBUG",
            "formatter": "verbose",
            "handlers": ["file"],
            "propagate": False,
        },
        "django.server": {
            "level": "INFO",
            "formatter": "verbose",
            "handlers": ["file"],
            "propagate": False,
        },
        'nplusone': {
            'handlers': ['console'],
            'level': 'WARN',
        },
    },
}
