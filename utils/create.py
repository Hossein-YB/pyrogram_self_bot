from .models import User, MessageInfo, ChannelTargetInfo, database


def create_tables():
    with database:
        database.create_tables([User, MessageInfo, ChannelTargetInfo, ])
