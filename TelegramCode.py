#####InBuildLibraries#####
import requests
import datetime 
import json
import random
import pickle
import re
import os.path

###########Telegram app API Key##############
api_key="2058218036:AAFo2iJ0oK1nkbj0-jEnJ25mcwYudUa0IiY"
###########################################
def GetLastMessage():
    url = "https://api.telegram.org/bot{}/getUpdates".format(api_key)
    response = requests.get(url)
    data=response.json()
    if(data['result']==[]):
        LastMessage="No Data"
        ChatId="No Data"
        UpdateId="No Data"
        return None
    else:
        LastMessage=data['result'][len(data['result'])-1]['message']['text']
        ChatId=data['result'][len(data['result'])-1]['message']['chat']['id']
        UpdateId=data['result'][len(data['result'])-1]['update_id']
        if len(data['result']) < 100:
            return LastMessage,ChatId,UpdateId
        else:
            print('offseting updates limit...')
            url = "https://api.telegram.org/bot{}/getUpdates?offset={}".format(api_key,UpdateId)
            response = requests.get(url)
            data=response.json()
            LastMessage=data['result'][len(data['result'])-1]['message']['text']
            ChatId=data['result'][len(data['result'])-1]['message']['chat']['id']
            UpdateId=data['result'][len(data['result'])-1]['update_id']
            return LastMessage,ChatId,UpdateId

#print("Hello Jegan")