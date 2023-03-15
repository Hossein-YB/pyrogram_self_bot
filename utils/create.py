from .models import MessageInfo, ChannelTargetInfo, database


def create_tables():
    with database:
        database.create_tables([MessageInfo, ChannelTargetInfo, ])
