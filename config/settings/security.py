import base64
from datetime import timedelta
from pathlib import Path

from .base import BASE_DIR, DEBUG, PRODUCTION, env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# Force HTTP to HTTPS redirection
SECURE_SSL_REDIRECT = True

# Enforce HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Secure cookies to prevent session hijacking
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Trust X-Forwarded-Proto header if behind a reverse proxy (Nginx/Heroku/AWS Cloudfront)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*'] if DEBUG else ['.ktbtracker.com', 'localhost', '127.0.0.1', '[::1]']

#
# Django OAuth Toolkit (DOT)
#
# OIDC_ISS_ENDPOINT is the OIDC Issuer endpoint (https://127.0.0.1, https://[test.]kingtigerblackbelt.com)
# OIDC_RSA_PRIVATE_KEYS is a a base64 encoded private key (base64 -w 0 < /etc/ssl/private/oidc.key)
#
OAUTH2_PROVIDER = {
    "OAUTH2_VALIDATOR_CLASS": "oauth2_provider.oauth2_validators.OAuth2Validator",
    "SECURE_SERVER": True,
    "ALLOWED_REDIRECT_URI_SCHEMES": ["https", "ktbtracker"],  # Allows 'ktbtracker://'
    "PKCE_REQUIRED": True,  # Globally enforce PKCE for added security
    # Core scopes required for JWT/OIDC
    "SCOPES": {
        "openid": "OpenID Connect scope",
        "read": "Read access",
        "write": "Write access",
    },
    # Set the OIDC Issuer endpoint (must use https://)
    "OIDC_ISS_ENDPOINT": env('OIDC_ISS_ENDPOINT'),
    # Supply your generated keys for RS256 signing
    "OIDC_RSA_PRIVATE_KEYS": [base64.b64decode(env('OIDC_RSA_PRIVATE_KEY')).decode('utf-8')],
}

SIMPLE_JWT = {
    # Use RSA-PSS 256-bit Signing
    "ALGORITHM": "PS256",
    "SIGNING_KEY": env("JWT_PRIVATE_KEY").replace("\\n", "\n"),
    "VERIFYING_KEY": env("JWT_PUBLIC_KEY").replace("\\n", "\n"),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    # Standard Simple JWT configs
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Authentication
#

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]
