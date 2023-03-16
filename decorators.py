from functools import wraps
from utils.models import User, MessageInfo


def user_is_under_supervision(func):
    async def check(clt, msg, *args, **kwargs):
        user_id = msg.chat.id
        user = User.get_supervision(user_id)
        if user:
            await func(clt, msg, *args, **kwargs)
        else:
            return False
    return check


def check_delete_msg(func):
    async def check(clt, msg, *args, **kwargs):
        for i in msg:
            msg_id = i.id
            message = MessageInfo.get_message(msg_id)
            if message:
                await func(clt, msg, message, *args, **kwargs)
            else:
                return False

    return check

