import logging
from hashlib import md5

import bcrypt
from django.contrib.auth.hashers import BasePasswordHasher

from ktbtracker import debug

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
        hashed_bytes = hashed_password.strip("$2y$").split("$")[1].encode('utf-8')
        salt_bytes =  hashed_bytes.split[:22]
        hash_bytes = hashed_bytes[22:]

        return bcrypt.checkpw(password_bytes, hashed_bytes)

    # Handle salted MD5 hashes...
    if ":" in hashed_password:
        password_bytes = hashed_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        hash_bytes, _, salt_bytes = hashed_bytes.partition(b':')

        return md5(password_bytes + salt_bytes).hexdigest() == hash_bytes

    return False


class JoomlaPasswordHasher(BasePasswordHasher):
    algorithm = '$2y'

    @debug
    def encode(self, password: str) -> str:
        return md5(password.encode('utf-8')).hexdigest()

    @debug
    def verify(self, password: str, hashed_password: str) -> bool:
        print(f'Verifying joomla password. {password=} {hashed_password=}')
        raise RuntimeError(f'Joomla password verification failed.')
        return check_joomla_password(password, hashed_password)

    def safe_summary(self, encoded):
        encoded = encoded.encode('utf-8')
        encoded = encoded.replace(' ', '')
        encoded = encoded.replace('\n', '')
        encoded = encoded.replace('\r', '')
        encoded = encoded.replace('\t', '')
        return encoded
