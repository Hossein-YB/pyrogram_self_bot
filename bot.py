from pyrogram import Client, filters, types
from pyrogram.errors import SessionPasswordNeeded

from os import remove

from texts import Messages
from account_info import API_ID, API_HASH, PHONE

from utils.models import User, MessageInfo, ChannelTargetInfo
from utils.create import create_tables
from decorators import user_is_under_supervision

msg_text = Messages()
create_tables()
app = Client("app", API_ID, API_HASH)


@app.on_message(filters.me & filters.private & filters.regex("^help$"))
async def command(clt: app, msg: types.Message):
    await msg.reply(msg_text.help_msg)


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


@app.on_message(filters.private & filters.text)
@user_is_under_supervision
async def message_user(clt: app, msg: types.Message):
    print(msg)
    text = msg.text
    chat_id = msg.from_user.id
    message_id = msg.id
    first_name = msg.chat.first_name
    datetime = msg.date
    MessageInfo.insert_message(user_id=chat_id, message_id=message_id, full_name=first_name,
                               message_text=text, datetime=datetime)


@app.on_message(filters.photo)
@user_is_under_supervision
async def save_timed_photo(clt: app, msg: types.Message):
    channel = ChannelTargetInfo.get_or_none(ChannelTargetInfo.user_id == msg.from_user.id)
    try:
        if msg.photo.ttl_seconds:
            if channel is not None:
                file_info = await app.download_media(msg, "media\\")
                user_info = await app.get_users(msg.from_user.id)
                print(file_info)
                if "jpg" in file_info:
                    await app.send_media_group(channel.channel_id, [
                        types.InputMediaPhoto(file_info, caption=msg_text.image_saved)
                    ])
                remove(file_info)

    except Exception as error:
        await app.send_message(chat_id=channel.channel_id, text=str(error.args))



if __name__ == "__main__":
    app.run()
