from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest


class FirebaseBackend(BaseBackend):

    def authenticate(self, request: HttpRequest, email: str = None, password: str = None) -> AbstractBaseUser | None:
        pass

    def get_user(self, user_id: int):
        pass

    def get_group(self, group_id):
        pass

    def get_groups(self, user_id):
        pass

    def get_permission(self, permission_id):
        pass

    def has_perm(self, perm, user_id):
        pass

    def has_module_perms(self, app_label, module_name):
        pass
