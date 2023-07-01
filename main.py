import time
from TelegramCode import *

print(api_key)

while 1:
    a=GetLastMessage()
    if(a):
        print(a,"Hello Tom Telegram bot is working")
    time.sleep(1)