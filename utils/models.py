from peewee import SqliteDatabase, Model, IntegerField, CharField, DateTimeField, BigIntegerField

database = SqliteDatabase('self_bot.db')


class BaseModel(Model):
    class Meta:
        database = database


class MessageInfo(BaseModel):
    user_id = BigIntegerField()
    message_id = BigIntegerField()
    full_name = CharField(max_length=100)
    message_text = CharField(max_length=2000)
    datetime = DateTimeField()

    @classmethod
    def insert_message(cls, user_id, message_id, full_name, message_text, datetime):
        q = cls.insert(user_id=user_id, message_id=message_id, full_name=full_name, message_text=message_text,
                       datetime=datetime, )
        q.execute()
        return True


class ChannelTargetInfo(BaseModel):
    user_id = BigIntegerField()
    channel_id = BigIntegerField()

    @classmethod
    def insert_channel(cls, user_id, channel_id):
        cls.insert(user_id=user_id, channel_id=channel_id, ).on_conflict_ignore(ignore=True)
        return True

    @classmethod
    def get_user_channel_id(cls, user_id):
        res = cls.get_or_none(cls.user_id == user_id)
        if res is None:
            return False
        else:
            return res.channel_id
