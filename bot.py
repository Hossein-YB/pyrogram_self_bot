from pyrogram import Client, filters, types

from os import remove

from texts import Messages
from account_info import API_ID, API_HASH
from tools import get_chat_and_message_id, get_media_file_id

from utils.models import User, MessageInfo, ChannelTargetInfo, MediaMessage
from utils.create import create_tables
from decorators import user_is_under_supervision, check_delete_msg

msg_text = Messages()
create_tables()
app = Client("app", API_ID, API_HASH)
path_download = 'media/'


@app.on_message(filters.me & filters.private & filters.regex("^help$"))
async def command(clt: app, msg: types.Message):
    await msg.reply(msg_text.help_msg)


async def send_file(file_id, chat_id):
    try:
        await app.send_document(chat_id, file_id)
        return True
    except Exception as error:
        return False


@app.on_message(filters.me & filters.private & filters.regex("^(دانلود|dnd)\n(https|http|t.me/)"))
async def command(clt: app, msg: types.Message):
    message_send_from = msg.chat.id
    chat_id, msg_id = get_chat_and_message_id(msg)
    message = await app.get_messages(chat_id=chat_id, message_ids=msg_id)
    file_info = get_media_file_id(message)
    if file_info:
        res = await send_file(file_info['file_id'], message_send_from)
        if res is False:
            file_loc = await app.download_media(message, path_download)
            await app.send_document(message_send_from, file_loc)
            remove(file_loc)
        else:
            return True
    else:
        await msg.reply(msg_text.is_not_media)


@app.on_message(filters.me & filters.private & filters.regex("^کپی"))
async def supervision(clt: app, msg: types.Message):
    chat_id, msg_id = get_chat_and_message_id(msg)
    message = await app.get_messages(chat_id=chat_id, message_ids=msg_id)
    await msg.reply(message.text)


@app.on_message(filters.me & filters.private & filters.regex("^نظارت$"))
async def supervision(clt: app, msg: types.Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    message_id = msg.id
    first_name = msg.chat.first_name
    User.insert_user(user_id=chat_id, under_supervision=True)
    channel = ChannelTargetInfo.get_or_none(ChannelTargetInfo.user_id == chat_id)
    await app.delete_messages(user_id, message_id)
    if channel is None:
        channel_crt = await app.create_channel(first_name, msg_text.text_url)
        ChannelTargetInfo.insert_channel(channel_id=channel_crt.id, user_id=chat_id)
        await app.send_message(channel_crt.id, msg_text.channel_msg.format(
                                           first_name, chat_id, msg_text.text_url))
    else:
        await app.send_message(channel.channel_id, msg_text.channel_ready)


@app.on_message(filters.me & filters.private & filters.regex("^لغو نظارت$"))
@user_is_under_supervision
async def unsupervised(clt: app, msg: types.Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    message_id = msg.id
    await app.delete_messages(user_id, message_id)
    channel = ChannelTargetInfo.get_or_none(ChannelTargetInfo.user_id == chat_id)
    if channel is not None:
        User.update(under_supervision=False)
        await app.send_message(channel.channel_id, msg_text.unsupervised)


async def save_timed_photo(clt: app, msg: types.Message):
    channel = ChannelTargetInfo.get_or_none(ChannelTargetInfo.user_id == msg.from_user.id)
    try:
        if msg.photo.ttl_seconds:
            if channel is not None:
                file_info = await app.download_media(msg, path_download)
                await app.send_photo(channel.channel_id, photo=file_info, caption=msg_text.image_saved)
                remove(file_info)
    except Exception as error:
        await app.send_message(chat_id=channel.channel_id, text=str(error.args))


async def save_timed_video(clt: app, msg: types.Message):
    channel = ChannelTargetInfo.get_or_none(ChannelTargetInfo.user_id == msg.from_user.id)
    try:
        if msg.video.ttl_seconds:
            if channel is not None:

                file_info = await app.download_media(msg, path_download)
                await app.send_video(channel.channel_id, video=file_info, caption=msg_text.video_saved)
                remove(file_info)
    except Exception as error:
        await app.send_message(chat_id=channel.channel_id, text=str(error.args))


async def get_media_info(clt, msg: types.Message):
    try:
        type_media = msg.media.name.lower()
        file_id = eval(f'msg.{str(type_media).lower()}.file_id')
        ttl = eval(f'msg.{str(type_media).lower()}.ttl_seconds')
        if ttl:
            if type_media == "photo":
                return await save_timed_photo(clt, msg)
            elif type_media == "video":
                return await save_timed_photo(clt, msg)

        caption = msg.caption
        MediaMessage.insert_media_message(message_id=msg.id, media_type=type_media, file_id=file_id, caption=caption)
        return True
    except Exception as error:
        print(str(error.args))
        return False


@app.on_message(filters.private & filters.text | filters.media)
@user_is_under_supervision
async def message_user(clt: app, msg: types.Message):
    media = msg.media if msg.media else None
    text = msg.text if msg.text else "media"
    chat_id = msg.from_user.id
    message_id = msg.id
    first_name = msg.chat.first_name
    datetime = msg.date
    MessageInfo.insert_message(user_id=chat_id, message_id=message_id, full_name=first_name,
                               message_text=text, datetime=datetime)
    if media:
        await get_media_info(clt, msg)


async def send_media(clt: app, msg: types.Message, message_id: int, channel: ChannelTargetInfo):
    media = MediaMessage.get_media(message_id)
    try:
        await app.send_message(channel.channel_id, msg_text.find_deleted_media)
        await app.send_cached_media(channel.channel_id, media.file_id, media.caption)
        MediaMessage.delete_media(media.id)
    except Exception as error:
        await app.send_message(channel.channel_id, str(error.args))


@app.on_deleted_messages()
@check_delete_msg
async def delete_message_user(clt: app, msg: types.Message, message: MessageInfo):

    channel = ChannelTargetInfo.get(ChannelTargetInfo.user_id == message.user_id)
    try:
        if message.message_text != 'media':
            if channel is not None:
                await app.send_message(channel.channel_id, msg_text.find_deleted_message.format(
                    message.full_name, message.datetime, message.message_text))
        else:
            await send_media(clt, msg, message.message_id, channel)
    except Exception as error:
        MessageInfo.delete_message(message)
        await app.send_message(chat_id=channel.channel_id, text=str(error.args))


@app.on_edited_message(filters.private)
@user_is_under_supervision
async def update_message_user(clt: app, msg: types.Message):
    channel = ChannelTargetInfo.get(ChannelTargetInfo.user_id == msg.from_user.id)
    try:
        get_message_info = MessageInfo.get(MessageInfo.message_id == msg.id)
        if get_message_info is not None:
            if channel is not None and get_message_info.message_text != msg.text:
                await app.send_message(channel.channel_id, msg_text.find_update_message.format(
                        get_message_info.full_name, get_message_info.datetime, get_message_info.message_text))

    except Exception as error:
        await app.send_message(chat_id=channel.channel_id, text=str(error.args))


if __name__ == "__main__":
    print("Bot is ready")
    app.run()
