from pyrogram import types


def check_media_type(msg: types.Message):
    typ = str(msg.media).split('.')[-1]
    if typ:
        return typ.lower()
    else:
        return None


def get_media_file_id(msg: types.Message):
    media_type = check_media_type(msg)
    if media_type is not None:
        file_id = eval('msg.' + media_type + '.file_id')
        file_info = {
            'media_type': media_type,
            'file_id': file_id,
        }
        return file_info
    else:
        return None
