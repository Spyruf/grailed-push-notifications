import time
import datetime
from threading import Thread
from colorama import Fore, Back, Style

import os
import sys
import json
import traceback

from selenium import webdriver
import selenium.common.exceptions
from bs4 import BeautifulSoup as bs
import redis

from dotenv import load_dotenv

load_dotenv()

import requests
from flask import Flask, request

redis_db = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
local = os.environ.get("LOCAL")


def send_message(recipient_id, message_text):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    url = "https://graph.facebook.com/v2.6/me/messages"

    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "messaging_type": "response",
        "message": {
            "text": message_text
        }
    })

    # r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    response = requests.request("POST", url, data=data, headers=headers, params=params)

    if response.status_code != 200:
        log(Fore.GREEN + response.status_code + Fore.RESET)
        print(Fore.GREEN + response.text + Fore.RESET)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = str(msg).format(*args, **kwargs)
            # msg = "test"
        print(u"{}: {}".format(datetime.datetime.now(), msg))
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


def get_IDs():
    task_names = redis_db.smembers('tasks')
    log(Fore.MAGENTA + "IDs are:" + Fore.RESET)

    id_set = set()

    for name in task_names:
        id = name.split('|')[0]
        url = name.split('|')[1]
        # log(Fore.MAGENTA + id + Fore.RESET)
        id_set.add(id)

    return id_set


if __name__ == '__main__':

    if input("Custom Message? Y/N: ") == "Y":
        message = input("What message would you like to send?\n")
    else:
        l1 = "Grailed Feed Notifications is back up and running! "
        l2 = "Sorry for any inconveniences during the last week, we are currently improving reliability and are planning to add new features soon! "
        l3 = ""
        message = l1 + l2 + l3

    print("The message is: ")
    print(message)

    if input("Test? Y/N: ") == "Y":
        log(Fore.CYAN + "Sending Test Message" + Fore.RESET)
        id = 2253201071372239
        send_message(id, message)

    elif input("Confirm? Y/N: ") == "Y":
        log(Fore.CYAN + "Sending Mass Message" + Fore.RESET)

        ids = get_IDs()
        for id in ids:
            log(Fore.MAGENTA + id + Fore.RESET)
            send_message(id, message)