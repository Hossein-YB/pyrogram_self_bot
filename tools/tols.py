def convert_chat_id(chat_id):
    try:
        chat_id = int('-100' + chat_id)
    except ValueError:
        chat_id = chat_id
    return chat_id
