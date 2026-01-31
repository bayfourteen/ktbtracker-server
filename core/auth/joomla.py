import logging
from hashlib import md5

import bcrypt
from django.contrib.auth.backends import ModelBackend, BaseBackend
from django.contrib.auth.models import User

from core import debug

logger = logging.getLogger(__name__)


@debug
def check_joomla_password(password: str, hashed_password: str) -> bool:
    """
    Determines if the provide password matches the joomla hashed password.

    Joomla passwords are either hashed using BCrypt (Blowfish) or via salted MD5.

    :return:
    """
    logger.info(f'Checking joomla password. {password=} {hashed_password=}')

    # Handle Bcrypt (Blowfish) hashes...
    if hashed_password.startswith("$2y$"):
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.strip("$2y$").encode('utf-8')

        return bcrypt.checkpw(password_bytes, hashed_bytes)

    # Handle salted MD5 hashes...
    if ":" in hashed_password:
        password_bytes = hashed_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        hash_bytes, _, salt_bytes = hashed_bytes.partition(b':')

        return md5(password_bytes + salt_bytes).hexdigest() == hash_bytes

    return False


class JoomlaAuthBackend(ModelBackend):
    @debug
    def authenticate(self, username=None, password=None, **kwargs):
        print(f'username={username}, password={password}')
        raise RuntimeError(f'username={username}, password={password}')
        try:
            user = User.objects.get(username=username)
            if check_joomla_password(password, user.password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None

    @debug
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
