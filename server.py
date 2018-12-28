import os
import zipfile
import binascii
from flask import Flask, render_template, request, session, redirect, jsonify
import ujson
import logging
from slackHelper import SlackHelper

app = Flask(__name__)

app.secret_key = binascii.hexlify(os.urandom(24))

# GZIP
COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/csv', 'text/xml', 'application/json',
                      'application/javascript']
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

allowed_commands = [
    'add'
    'help'
    'remove'
    'my-words'
]


@app.route('/sub', methods=['POST', 'GET'])
def hello_world():
    dic = ujson.load(open('data.json'))
    print(dic['users'])

    return ''


@app.route('/bot', methods=['POST', 'GET'])
def add():
    slackhelper = SlackHelper()
    command_text = request.form['text']
    command_text = command_text.split(' ')
    slack_uid = request.form['user_id']
    response_body = {}

    if command_text[0] not in allowed_commands:
        response_body = {'text': 'Invalid Command Sent - type `/an help` for available commands'}

    if command_text[0] == 'help':
        response_body = dohelp()
    if command_text[0] == 'add':
        response_body = doadd(slack_uid, command_text[1])
    if command_text[0] == 'remove':
        response_body = dorm(slack_uid, command_text[1])
    if command_text[0] == 'my-words':
        response_body = doshow(slack_uid)

    response = jsonify(response_body)
    response.status_code = 200
    return response


def dohelp():
    return {"text": " Available commands : \n " +
                    "`add keyword` to add a keyword in your list (and register you if its your first time, \n " +
                    "`remove keyword` to remove a keyword from your list, \n" +
                    "`my-words` to display all the keywords in your list, \n" +
                    "`help` to display help"
            }


def doadd(user, word):
    dic = ujson.load(open('data.json'))
    if not checkindb(user):
        dic[user] = []

    if word not in dic[user]:
        dic[user].append(word)
        savedb(dic)
        return {"text": " Your word : `" + word + "` have successfully been added to our database. If you want to see all your words type `/an my-words`. If you want to remove this word type `/an remove " + word + "`"}
    else:
        return {"text": " The keyword `" + word + "` is already in our database please use the command `/an my-words` to see which words you already added"}


def dorm(user, word):
    dic = ujson.load(open('data.json'))
    if not checkindb(user):
        return {"text": ' You are not referenced in our database. Please type `/an add {keyword}` to make your first entry in our database.'}
    else:
        if word not in dic[user]:
            return {"text": " The keyword `" + word + "` is not in our database please use the command `/an my-words` to see which words you already added"}
        else:
            dic[user].remove(word)
            savedb(dic)
            return {"text": " The keyword `" + word + "` have successfully been removed from our database"}


def doshow(user):
    dic = ujson.load(open('data.json'))
    if not checkindb(user):
        return {"text": ' You are not referenced in our database. Please type `/an add {keyword}` to make your first entry in our database.'}
    elif len(dic[user]) == 0:
        return {"text": "You do not have any words, please type `/an add {keyword}` to add a word"}
    else:
        words = "["
        for w in dic[user]:
            words += w + ','
        words = words[:-1] + ']'
        return {"text": "Our dataset contains the following words : `" + words + "`"}


def checkindb(user):
    dic = ujson.load(open('data.json'))

    return user in dic


def savedb(data):
    ujson.dump(data, open('data.json', 'w'))





if __name__ == '__main__':
    app.run()
