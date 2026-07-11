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

# Django OAuth Toolkit (DOT)
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
    "OIDC_RSA_PRIVATE_KEYS": [env('OIDC_RSA_PRIVATE_KEY')],
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
