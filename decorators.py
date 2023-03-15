from functools import wraps
from utils.models import User


def user_is_under_supervision(func):

    async def check(clt, msg, *args, **kwargs):
        user_id = msg.chat.id
        user = User.get_supervision(user_id)
        if user:
            await func(clt, msg, *args, **kwargs)
        else:
            return False
    return check

