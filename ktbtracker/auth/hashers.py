import logging
from hashlib import md5

import bcrypt
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.translation import gettext_lazy as _

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
    if hashed_password.startswith("joomla$$2y$"):
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.strip("joomla$").encode('utf-8')

        return bcrypt.checkpw(password_bytes, hashed_bytes)

    # Handle salted MD5 hashes...
    if ":" in hashed_password:
        password_bytes = hashed_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        hash_bytes, _, salt_bytes = hashed_bytes.partition(b':')

        return md5(password_bytes + salt_bytes).hexdigest() == hash_bytes

    return False


class JoomlaPasswordHasher(BasePasswordHasher):
    # joomla$$2y $ 10 $ xxxxxxxxx
    algorithm = 'joomla$'

    def decode(self, encoded):
        algorithm, iterations, salt, hash = encoded.strip("joomla$$").split("$", 3)
        assert algorithm == self.algorithm
        return {
            "algorithm": algorithm,
            "hash": hash,
            "iterations": int(iterations),
            "salt": salt,
        }

    @debug
    def encode(self, password: str) -> str:
        return md5(password.encode('utf-8')).hexdigest()

    @debug
    def verify(self, password: str, hashed_password: str) -> bool:
        print(f'Verifying joomla password. {password=} {hashed_password=}')
        raise RuntimeError(f'Joomla password verification failed.')
        return check_joomla_password(password, hashed_password)

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            _("algorithm"): decoded["algorithm"],
            _("iterations"): decoded["iterations"],
            _("salt"): mask_hash(decoded["salt"]),
            _("hash"): mask_hash(decoded["hash"]),
        }
