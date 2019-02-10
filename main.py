import requests, re, json
from bottle import run, post, response, request as bottle_request
from pymongo import MongoClient, ASCENDING
from answers import ANSWERS, answer
from config import CONFIG
from commands import COMMANDS
from top import top_score, top_leaderboard

BOT_URL = 'https://api.telegram.org/bot' + CONFIG['TELEGRAM_API_KEY'] + '/'

def get_message(data):
    """
    Extract message data from a telegram update.
    """
    if (data.get('edited_message', '') != ''):
        return data['edited_message']
    else:
        return data['message']

def get_chat_id(data):  
    """
    Method to extract chat id from telegram update.
    """
    return str(get_message(data)['chat']['id'])

def get_message_author(data):
    """
    Extract the author's first name and identifier from a telegram update.
    """
    message = get_message(data)

    user_name = message['from']['first_name']
    user_id = message['from']['id']
    return user_name, user_id

def send_message(prepared_data):  
    """
    Prepared data should be json which includes at least `chat_id` and `text`
    """ 
    message_url = BOT_URL + 'sendMessage'
    requests.post(message_url, json=prepared_data)


def prepare_data_for_answer(data, content):
    json_data = {
        "chat_id": get_chat_id(data),
        "text": content,
    }

    return json_data

def get_message_text(data):  
    """
    Extract message text from a telegram update.
    """
    message = get_message(data)
    message_text = ''
    
    if (message.get('text', '')):
        message_text = message['text']

    return message_text

def init_db():
    """
    Initiate database connection, create indices
    """
    client = MongoClient(CONFIG['MONGO_HOST'], CONFIG['MONGO_PORT'])
    db = client[CONFIG['DB_NAME']]
    disable_for_chat_collection = db[CONFIG['DB_DISABLE_COLLECTION']]
    disable_for_chat_collection.create_index([('chat_id', ASCENDING)], unique=True, background=True)

    top_collection = db[CONFIG['DB_TOP_COLLECTION']]
    top_collection.create_index([('chat_id', ASCENDING), ('author_id', ASCENDING)], unique=True, background=True)

    return disable_for_chat_collection, top_collection

def get_disabled(collection, chat_id):
    """
    Database exploration to find out whether the bot is disabled for the chat passed as argument
    """
    disabled_doc = collection.find_one({'chat_id': chat_id})
    if (disabled_doc is None):
        print("no disable for this chat")
        disabled_doc = {
            'chat_id': chat_id,
            'disabled': False
        }
        collection.insert_one(disabled_doc)
    return disabled_doc

@post('/')
def main():
    disable_for_chat_collection, top_collection = init_db()

    data = bottle_request.json
    text = get_message_text(data)
    chat_id = get_chat_id(data)

    disabled_doc = get_disabled(disable_for_chat_collection, chat_id)

    if disabled_doc['disabled']:
        # Enable the bot for the current chat
        if COMMANDS["ENABLE"]["RE"].search(text):
            answer_content = answer("ENABLE")
            disable_for_chat_collection.find_one_and_update({ 'chat_id': chat_id }, { '$set': { 'disabled': False } })
            answer_data = prepare_data_for_answer(data, answer_content)
            send_message(answer_data)
            return response


    if not disabled_doc['disabled']:
        # Disables the bot for the current chat
        if COMMANDS["DISABLE"]["RE"].search(text):
            answer_content = answer("DISABLE")
            disable_for_chat_collection.find_one_and_update({ 'chat_id': chat_id }, { '$set': { 'disabled': True } })
            answer_data = prepare_data_for_answer(data, answer_content)
            send_message(answer_data)
            return response 

        # Someone scored
        if (COMMANDS['TOPSCORE']["RE"].search(text)):
            author, author_id = get_message_author(data)
            
            answer_content = top_score(top_collection, author_id, chat_id, author)

            answer_data = prepare_data_for_answer(data, answer_content)
            send_message(answer_data)
            return response

        # Someone asks for the leaderboard
        if (COMMANDS['TOP']["RE"].search(text)):
            answer_content = top_leaderboard(top_collection, chat_id)
            
            answer_data = prepare_data_for_answer(data, answer_content)
            send_message(answer_data)
            return response

        # Other commands
        for key, value in COMMANDS.items():
            if COMMANDS[key]['RE'].search(text) and not key == 'ENABLE':
                answer_content = COMMANDS[key]['FUNCTION'](ANSWERS[key])
                answer_data = prepare_data_for_answer(data, answer_content)
                send_message(answer_data)
                return response

if __name__ == '__main__':  
    run(host='localhost', port=8080, debug=True)