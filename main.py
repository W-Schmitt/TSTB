import requests
import re
from bottle import run, post, response, request as bottle_request
import pickle
import json
import os
from pymongo import MongoClient, ASCENDING
from answers import answer
from config import CONFIG
from commands import RE
from top import top_score, top_leaderboard

BOT_URL = 'https://api.telegram.org/bot' + CONFIG['TELEGRAM_API_KEY'] + '/'

def get_chat_id(data):  
    """
    Method to extract chat id from telegram request.
    """
    if (data.get('edited_message', '') != ''):
        chat_id = data['edited_message']['chat']['id']
    else:
        chat_id = data['message']['chat']['id']

    return chat_id

def get_message_author(data):
    """
    Retrieves a user's first name and identifier from a telegram message object
    """
    if (data.get('edited_message', '') != ''):
        user_name = data['edited_message']['from']['first_name']
        user_id = data['edited_message']['from']['id']
    else:
        user_name = data['message']['from']['first_name']
        user_id = data['message']['from']['id']

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

def get_message(data):  
    """
    Method to extract message id from telegram request.
    """
    message_text = ''
    if (data.get('edited_message', '') != ''):
        message_text = data['edited_message']['text']    
    elif (data.get('message', '') != ''): 
        if (data['message'].get('text', '')):
            message_text = data['message']['text']
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
    text = get_message(data)
    chat_id = str(get_chat_id(data))

    disabled_doc = get_disabled(disable_for_chat_collection, chat_id)

    if disabled_doc['disabled']:
        # Enable the bot for the current chat
        if RE["ENABLE"].search(text):
            answer_content = answer("ENABLE")
            disable_for_chat_collection.find_one_and_update({ 'chat_id': chat_id }, { '$set': { 'disabled': False } })
            answer_data = prepare_data_for_answer(data, answer_content)
            send_message(answer_data)
            return response


    if not disabled_doc['disabled']:
        # Disables the bot for the current chat
        if RE["DISABLE"].search(text):
            answer_content = answer("DISABLE")
            disable_for_chat_collection.find_one_and_update({ 'chat_id': chat_id }, { '$set': { 'disabled': True } })
            answer_data = prepare_data_for_answer(data, answer_content)
            send_message(answer_data)
            return response 

        # Someone scored
        if (RE['TOPSCORE'].search(text)):
            author, author_id = get_message_author(data)
            
            answer_content = top_score(top_collection, author_id, chat_id, author)

            answer_data = prepare_data_for_answer(data, answer_content)
            send_message(answer_data)
            return response

        # Someone asks for the leaderboard
        if (RE['TOP'].search(text)):
            answer_content = top_leaderboard(top_collection, chat_id)
            
            answer_data = prepare_data_for_answer(data, answer_content)
            send_message(answer_data)
            return response

        # Other commands
        for key, value in RE.items():
            if RE[key].search(text) and not key == 'ENABLE':
                answer_content = answer(key)
                answer_data = prepare_data_for_answer(data, answer_content)
                send_message(answer_data)
                return response

if __name__ == '__main__':  
    run(host='localhost', port=8080, debug=True)