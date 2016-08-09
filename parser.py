# -*- coding: utf-8 -*-

import os
import requests
from dateutil import parser

from datasources.sources import AtomSource, RssSource, TwitterSource

# Contants
BOT_ID = 'ADD_BOT_ID_HERE'
BOT_URL = u"http://api.telegram.org/bot%s/sendMessage" % BOT_ID
BOT_CHANNEL = "@HackLabAlmeriaNoticias"
GROUP_ID = '-137038280'
LAST_ITEM_PATH = 'last_item'

# Config
PARSE_ONLY_NEW = True
SOURCES = [
    AtomSource('http://hacklabalmeria.net/atom.xml'),
    RssSource('https://foro.hacklabalmeria.net/c/observatorio.rss'),
    TwitterSource('https://twitrss.me/twitter_user_to_rss/?user=hacklabal')
]

# Properties
lastItemFile = None
lastParsedDate = None

if PARSE_ONLY_NEW:
    if os.path.isfile(LAST_ITEM_PATH):
        lastItemFile = open(LAST_ITEM_PATH, 'r+')

    if lastItemFile:
        contents = lastItemFile.readline()
        if contents:
            lastParsedDate = parser.parse(contents)
        lastItemFile.seek(0)
    else:
        lastItemFile = open(LAST_ITEM_PATH, 'w')

messages = []

for source in SOURCES:
    # Parse and merge all messages
    messages += filter(None, source.parse(lastParsedDate))

# Sort by date ASC
sortedMessages = sorted(messages, key=lambda message: message.date)

# Send all messages to channel
# TODO Add 'Senders'
# TODO Maybe add a delay?
botHttpRequest = requests.Session()
for message in sortedMessages:
    url = BOT_URL

    # Send to Channel
    postBody = { 'chat_id' : BOT_CHANNEL,
                 'text' : message.text,
                 'parse_mode' : 'HTML'}

    botHttpRequest.request(url=url, method='POST', data=postBody)

    # Send to group
    postBody = {'chat_id': GROUP_ID,
                'text': message.text,
                'parse_mode': 'HTML'}

    response = botHttpRequest.request(url=url, method='POST', data=postBody)

    if response.status_code == 400:
        print("Error (" + response.text + ") on message: \n"+message.text+"\n\n")
    else:
        # Only save date from the last message that was sent correctly
        lastParsedDate = message.date
        print(str(response.status_code) + ": " + response.text)

if lastParsedDate:
    lastItemFile.write(lastParsedDate.isoformat())

lastItemFile.close()