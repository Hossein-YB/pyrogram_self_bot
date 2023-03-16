from peewee import SqliteDatabase, Model, IntegerField, CharField, DateTimeField, BigIntegerField, BooleanField
from peewee import ForeignKeyField

database = SqliteDatabase('self_bot.db')


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    user_id = BigIntegerField(primary_key=True)
    under_supervision = BooleanField(default=False)

    @classmethod
    def insert_user(cls, user_id, under_supervision):
        q = cls.insert(user_id=user_id, under_supervision=under_supervision).on_conflict_ignore(ignore=True)
        q.execute()
        return True

    @classmethod
    def get_supervision(cls, user_id):
        user = cls.get_or_none(cls.user_id == user_id)
        if user is not None:
            return user.under_supervision
        else:
            return False


class MessageInfo(BaseModel):
    user_id = ForeignKeyField(User, User.user_id, on_delete="CASCADE")
    message_id = BigIntegerField()
    full_name = CharField(max_length=100)
    message_text = CharField(max_length=2000, null=True)
    datetime = DateTimeField()

    @classmethod
    def insert_message(cls, user_id, message_id, full_name, message_text, datetime):
        q = cls.insert(user_id=user_id, message_id=message_id, full_name=full_name, message_text=message_text,
                       datetime=datetime, )
        q.execute()
        return True

    @classmethod
    def get_message(cls, msg_id):
        msg = cls.get_or_none(cls.message_id == msg_id)
        if msg is not None:
            return msg
        else:
            return False

    @classmethod
    def delete_message(cls, msg):
        try:
            cls.delete_by_id(msg.id)
        except Exception as error:
            print(error.args)


class MediaMessage(BaseModel):
    message_id = ForeignKeyField(MessageInfo, MessageInfo.message_id, on_delete="CASCADE", related_name="medias")
    media_type = CharField(max_length=15)
    file_id = CharField(max_length=1000)
    caption = CharField(max_length=2000, null=True)

    @classmethod
    def insert_media_message(cls, message_id, media_type, file_id, caption):
        q = cls.insert(message_id=message_id, media_type=media_type, file_id=file_id, caption=caption,)
        q.execute()
        return True

    @classmethod
    def get_media(cls, msg_id):
        msg = cls.get_or_none(cls.message_id == msg_id)
        if msg is not None:
            return msg
        else:
            return False

    @classmethod
    def delete_media(cls, rec_id):
        try:
            cls.delete_by_id(rec_id)
        except Exception as error:
            print(error.args)


class ChannelTargetInfo(BaseModel):
    user_id = ForeignKeyField(User, User.user_id, on_delete="CASCADE")
    channel_id = BigIntegerField()

    @classmethod
    def insert_channel(cls, user_id, channel_id):
        q = cls.insert(user_id=user_id, channel_id=channel_id, ).on_conflict_ignore(ignore=True)
        q.execute()
        return True

    @classmethod
    def get_user_channel_id(cls, user_id):
        res = cls.get_or_none(cls.user_id == user_id)
        if res is None:
            return False
        else:
            return res.channel_id
