from django.contrib.auth.backends import ModelBackend
from .dbmanager import DbManager
from .models import User


class LoginBackend(ModelBackend):
    db_manager = DbManager()

    def authenticate(self, request, username=None, password=None, **kwargs):

        user = self.db_manager.get_user_by_username(username=username)
        # print(f" i am inside the back end {username}, {password}")
        if user and user.password == password:
                return user
        else:
            return None


def get_user(self, user_id):

    try:
        return self.db_manager.get_user_by_id(user_id)
    except self.db_manager.get_user_by_id(user_id).rowcount == 0:
        return None
