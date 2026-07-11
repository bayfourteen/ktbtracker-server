import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from ktbtracker.utils import debug


# Get the logger instance
logger = logging.getLogger("django")


@debug
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Fetch user IP address safely
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    logger.info(
        f"User login successful: ID={user.id}, Username={user.username}, IP={ip}"
    )


@debug
@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'Unknown')
    logger.warning(f"Failed login attempt for username: {username}")
