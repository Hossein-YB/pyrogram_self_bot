def convert_chat_id(chat_id):
    try:
        chat_id = int('-100' + chat_id)
    except ValueError:
        chat_id = chat_id
    return chat_id


def get_chat_and_message_id(msg):
    url = msg.text.split('\n')[1]
    url = url.split('/')
    chat_id, msg_id = convert_chat_id(url[-2]), int(url[-1])
    return chat_id, msg_id

