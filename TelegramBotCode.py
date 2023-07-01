#####InBuildLibraries#####
import requests
import datetime 
import json
import random
import pickle
import re
import os.path
#####Need to Install Libraries####
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import numpy
import tflearn
import tensorflow
#####UserDefinedLibraries####
from MealPlanningCode import *
from GoogleCalendarCode import *
from DatabaseEditCode import *
from IntentTrainer import *

###########Telegram app API Key##############
api_key="2058218036:AAFo2iJ0oK1nkbj0-jEnJ25mcwYudUa0IiY"
###########################################

#############CurrentDirectory#######################
CodeDirectory=os.path.dirname(os.path.realpath(__file__))
MainDirectory=os.path.dirname(CodeDirectory)

###########Dialogs JSON File##############
DialogsJsonFile=MainDirectory+"/JsonFiles/Dialogs.json"
with open(DialogsJsonFile) as file:
    Dialogs = json.load(file)
###########################################
global IntentModel
###########Intent Model File##############
TrainedWordsPickleFile=MainDirectory+"/PickleFiles/TrainedWords.pickle"
IntentModelFile=MainDirectory+"/IntentsModel/IntentModel.tflearn"
def LoadModelFile():
    global IntentModel
    global words
    global labels
    global training
    global output
    try:
        with open(TrainedWordsPickleFile, "rb") as f:
            words, labels, training, output = pickle.load(f)
        tensorflow.compat.v1.reset_default_graph()
        net = tflearn.input_data(shape=[None, len(training[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
        net = tflearn.regression(net)
        IntentModel = tflearn.DNN(net)
        IntentModel.load(IntentModelFile)
        print("Loading Intent Model")
    except:
        print("Saving Intent Model")
        IntentTrain()
        LoadModelFile()
        
###########################################
    
##################Telegram Functions##############################################
def GetLastMessage():
    url = "https://api.telegram.org/bot{}/getUpdates".format(api_key)
    response = requests.get(url)
    data=response.json()
    if(data['result']==[]):
        LastMessage="No Data"
        ChatId="No Data"
        UpdateId="No Data"
        return LastMessage,ChatId,UpdateId
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
        
def SendMessage(ChatId,ReplyMessage):
    url='https://api.telegram.org/bot'+str(api_key)+'/sendMessage?text='+str(ReplyMessage)+'&chat_id='+str(ChatId)
    response = requests.get(url)
    #return response

def SendMessageWithButtons(ChatId,ReplyMessage,Keyboard):
    key=json.JSONEncoder().encode(Keyboard)
    url='https://api.telegram.org/bot'+str(api_key)+'/sendmessage?chat_id='+str(ChatId)+'&text='+str(ReplyMessage)+'&reply_markup='+key
    response = requests.get(url)
    #return response

def DayKeyBoard():
    Keyboard={'keyboard': [[{'text':'today'}],
                                       [{'text':'tomorrow'},{'text':'yesterday'}],
                                       [{'text':'day after tomorrow'}],
                                       [{'text':'day before yesterday'}],
                                       [{'text':'sunday'}],
                                       [{'text':'monday'},{'text':'tuesday'}],
                                       [{'text':'wednesday'},{'text':'thursday'}],
                                       [{'text':'friday'},{'text':'saturday'}],
                                       [{'text':'last sunday'}],
                                       [{'text':'last monday'}],
                                       [{'text':'last tuesday'}],
                                       [{'text':'last wednesday'}],
                                       [{'text':'last thursday'}],
                                       [{'text':'last friday'}],
                                       [{'text':'last saturday'}],
                                       [{'text':'MainMenu'}],
                                      ]
                              }
    return Keyboard

def WeekDayKeyBoard():
    Keyboard={'keyboard': [[{'text':'sunday'}],
                           [{'text':'monday'},{'text':'tuesday'}],
                           [{'text':'wednesday'},{'text':'thursday'}],
                           [{'text':'friday'},{'text':'saturday'}],
                           [{'text':'MainMenu'}],
                          ]
                      }
    return Keyboard

def GetKeyboard(List):
    Keyboard={'keyboard': [
                          ]
              }
    for i in List:
        Keyboard['keyboard'].append([{'text':i}])
    Keyboard['keyboard'].append([{'text':'MainMenu'}])
    return Keyboard

def ShowPlan(PreviousLastMessage,ChatId,PreviousUpdateId):
    ReplyMessage="Select dayplan or week plan or Month plan"
    Keyboard={'keyboard': [[{'text':'Day Plan'}],
                           [{'text':'Week Plan'}],
                           [{'text':'MainMenu'}],
                          ]
              }
    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
    while True:
        CurrentLastMessage,ChatId,CurrentUpdateId=GetLastMessage()
        if PreviousLastMessage==CurrentLastMessage and CurrentUpdateId==PreviousUpdateId:
            print('continue1')
            continue
        else:
            print("ShowPlan:",CurrentLastMessage)
            if(CurrentLastMessage=="MainMenu"):
                main()
            results = IntentModel.predict([bag_of_words(CurrentLastMessage, words)])
            results_index = numpy.argmax(results)
            if(results[0][results_index])>0.8:
                tag = labels[results_index]
            if(CurrentLastMessage in ['Day Plan','Week Plan','Month Plan']):
                tag=CurrentLastMessage
                
            elif(CurrentLastMessage in ["today","tomorrow","yesterday","day after tomorrow","day before yesterday",
               "last sunday","last monday","last tuesday","last wednesday","last thursday","last friday","last saturday",
               "sunday","monday","tuesday","wednesday","thursday","friday","saturday",
               "next sunday","next monday","next tuesday","next wednesday","next thursday","next friday","next saturday"]):
                tag='ShowDayPlan'
            elif(CurrentLastMessage in ['this week','last week','next week']):
                tag="ShowWeekPlan"
            elif(CurrentLastMessage in ['this month','last month','next month']):
                tag="ShowMonthPlan"
            else:
                tag = None
                
            if(tag=='Day Plan'):
                print("Came here")
                ReplyMessage="Tell me the day if its Date, Type in format(dd.mm.YYYY)"
                Keyboard=DayKeyBoard()
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
            if(tag=='Week Plan'):
                ReplyMessage="Select dayplan or week plan or Month plan"
                Keyboard={'keyboard': [[{'text':'this week'}],
                                       [{'text':'last week'}],
                                       [{'text':'next week'}],
                                       [{'text':'MainMenu'}],
                                      ]
                          }
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                
            if(tag=='ShowDayPlan'):
                ReplyMessage=ShowDayPlan(CurrentLastMessage)
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
                return "Dayplan has Shown",CurrentLastMessage,ChatId,CurrentUpdateId
            if(tag=='ShowWeekPlan'):
                ReplyMessage=ShowWeekPlan(CurrentLastMessage)
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
                return "WeekPlan has Shown",CurrentLastMessage,ChatId,CurrentUpdateId
        PreviousLastMessage=CurrentLastMessage
        PreviousUpdateId=CurrentUpdateId

def PostpondPlan(PreviousLastMessage,ChatId,PreviousUpdateId):
    ReplyMessage="Tell me the day if its Date, Type in format(dd.mm.YYYY)"
    Keyboard=DayKeyBoard()
    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
    while True:
        TodayDate=datetime.datetime.now()
        CurrentLastMessage,ChatId,CurrentUpdateId=GetLastMessage()
        if PreviousLastMessage==CurrentLastMessage and CurrentUpdateId==PreviousUpdateId:
            print('continue2')
            continue
        else:
            print("Postpond:",CurrentLastMessage)
            if(CurrentLastMessage=="MainMenu"):
                main()
            results = IntentModel.predict([bag_of_words(CurrentLastMessage, words)])
            results_index = numpy.argmax(results)
            if(results[0][results_index])>0.8:
                tag = labels[results_index]    
            if(CurrentLastMessage in ["today","tomorrow","yesterday","day after tomorrow","day before yesterday",
               "last sunday","last monday","last tuesday","last wednesday","last thursday","last friday","last saturday",
               "sunday","monday","tuesday","wednesday","thursday","friday","saturday",
               "next sunday","next monday","next tuesday","next wednesday","next thursday","next friday","next saturday"]):
                tag='Days'
            elif(CurrentLastMessage in ["MainDish","Combo1","Combo2","Sidedish1","Sidedish2"]):
                tag="DishType"
            else:
                tag = None
            try:
                StartDate=datetime.datetime.strptime(CurrentLastMessage,"%d.%m.%Y" )
                ReplyMessage="Select Dish Type to postpond"
                Keyboard={'keyboard': [[{'text':'MainDish'}],
                                       [{'text':'Combo1'}],
                                       [{'text':'Combo2'}],
                                       [{'text':'Sidedish1'}],
                                       [{'text':'Sidedish2'}],
                                       [{'text':'MainMenu'}],
                                      ]
                          }
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                PostPondDataFlag[0]=1
            except:
                pass
            
            if(tag=="Days"):
                EventDate=ChooseDate(CurrentLastMessage)
            
                StartDate=EventDate
                ReplyMessage="Select Dish Type to postpond"
                Keyboard={'keyboard': [[{'text':'MainDish'}],
                                       [{'text':'Combo1'}],
                                       [{'text':'Combo2'}],
                                       [{'text':'Sidedish1'}],
                                       [{'text':'Sidedish2'}],
                                       [{'text':'MainMenu'}],
                                      ]
                          }
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
            
            if(tag=="DishType"):    
                LastDate=LastPlannedDate()
                MealType="Lunch"
                Dish=GetData(StartDate,MealType,CurrentLastMessage)
                Temp1=Dish
                UpdateData(StartDate,MealType,CurrentLastMessage,"Postponed")
                NextDate=StartDate+timedelta(days=7)
                while (NextDate<=LastDate):
                    Temp2=GetData(NextDate,MealType,CurrentLastMessage)
                    UpdateData(NextDate,MealType,CurrentLastMessage,Temp1)
                    Temp1=Temp2
                    NextDate+=timedelta(days=7)
                return "Postpond Sucessfully",CurrentLastMessage,ChatId,CurrentUpdateId
        PreviousLastMessage=CurrentLastMessage
        PreviousUpdateId=CurrentUpdateId

def Interchange(PreviousLastMessage,ChatId,PreviousUpdateId):
    ReplyMessage="Tell me the Start day if its Date, Type in format(dd.mm.YYYY)"
    Keyboard=DayKeyBoard()
    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
    StartDayFlag=0
    EndMealType=None
    while True:
        TodayDate=datetime.datetime.now()
        CurrentLastMessage,ChatId,CurrentUpdateId=GetLastMessage()
        if PreviousLastMessage==CurrentLastMessage and CurrentUpdateId==PreviousUpdateId:
            if(EndMealType!=None):
                StartDish=GetData(StartDate,StartMealType,DishType)
                EndDish=GetData(EndDate,EndMealType,DishType)
                print(StartDish,EndDish)
                UpdateData(StartDate,StartMealType,DishType,EndDish)
                UpdateData(EndDate,EndMealType,DishType,StartDish)
                return "Interchange Success",CurrentLastMessage,ChatId,CurrentUpdateId
            print('continue3')
            continue
        else:
            print("InterChange:",CurrentLastMessage)
            if(CurrentLastMessage=="MainMenu"):
                main()
            results = IntentModel.predict([bag_of_words(CurrentLastMessage, words)])
            results_index = numpy.argmax(results)
            if(results[0][results_index])>0.8:
                tag = labels[results_index]
            if(CurrentLastMessage in ["today","tomorrow","yesterday","day after tomorrow","day before yesterday",
                   "last sunday","last monday","last tuesday","last wednesday","last thursday","last friday","last saturday",
                   "sunday","monday","tuesday","wednesday","thursday","friday","saturday",
                   "next sunday","next monday","next tuesday","next wednesday","next thursday","next friday","next saturday"]):
                tag="Days"
            elif(CurrentLastMessage in ["Breakfast","Lunch","Dinner"]):
                tag="MealType"
            elif(CurrentLastMessage in ["MainDish","Combo1","Combo2","Sidedish1","Sidedish2"]):
                tag="DishType"
            else:
                tag = None
            try:
                Date=datetime.datetime.strptime(CurrentLastMessage,"%d.%m.%Y" )
                tag="Date"
            except:
                pass
            
            if(tag=="Days"):
                EventDate=ChooseDate(CurrentLastMessage)
                if(StartDayFlag==0):
                    StartDate=EventDate
                    StartDayFlag=1
                    ReplyMessage="Select MealType Type to Interchange"
                    Keyboard={'keyboard': [[{'text':'Breakfast'}],
                                           [{'text':'Lunch'}],
                                           [{'text':'Dinner'}],
                                           [{'text':'MainMenu'}],
                                          ]
                              }
                    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                elif(StartDayFlag==1):
                    EndDate=EventDate
                    StartDayFlag=0
                    ReplyMessage="Select MealType Type to Interchange"
                    Keyboard={'keyboard': [[{'text':'Breakfast'}],
                                           [{'text':'Lunch'}],
                                           [{'text':'Dinner'}],
                                           [{'text':'MainMenu'}],
                                          ]
                              }
                    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                    
            if(tag=="Date"):
                if(StartDayFlag==0):
                    StartDate=Date
                    StartDayFlag=1
                    ReplyMessage="Select MealType Type to Interchange"
                    Keyboard={'keyboard': [[{'text':'Breakfast'}],
                                           [{'text':'Lunch'}],
                                           [{'text':'Dinner'}],
                                           [{'text':'MainMenu'}],
                                          ]
                              }
                    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                elif(StartDayFlag==1):
                    EndDate=Date
                    StartDayFlag=0
                    ReplyMessage="Select MealType Type to Interchange"
                    Keyboard={'keyboard': [[{'text':'Breakfast'}],
                                           [{'text':'Lunch'}],
                                           [{'text':'Dinner'}],
                                           [{'text':'MainMenu'}],
                                          ]
                              }
                    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
            if(tag=="MealType"):
                if(StartDayFlag==1):
                    StartMealType=CurrentLastMessage
                    ReplyMessage="Select Dish Type to Interchange"
                    Keyboard={'keyboard': [[{'text':'MainDish'}],
                                           [{'text':'Combo1'}],
                                           [{'text':'Combo2'}],
                                           [{'text':'Sidedish1'}],
                                           [{'text':'Sidedish2'}],
                                           [{'text':'MainMenu'}],
                                          ]
                              }
                    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                if(StartDayFlag==0):
                    EndMealType=CurrentLastMessage
            if(tag=="DishType"):
                DishType=CurrentLastMessage
                ReplyMessage="Tell me the End day if its Date, Type in format(dd.mm.YYYY)"
                Keyboard=DayKeyBoard()
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                
                
        PreviousLastMessage=CurrentLastMessage
        PreviousUpdateId=CurrentUpdateId     

def ShowFoodItems(PreviousLastMessage,ChatId,PreviousUpdateId):
    ReplyMessage="Tell me the  day if its Date, Type in format(dd.mm.YYYY)"
    Keyboard={'keyboard': [[{'text':'sunday'}],
                           [{'text':'monday'},{'text':'tuesday'}],
                           [{'text':'wednesday'},{'text':'thursday'}],
                           [{'text':'friday'},{'text':'saturday'}],
                           [{'text':'MainMenu'}],
                          ]
                  }
    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
    while True:
        TodayDate=datetime.datetime.now()
        CurrentLastMessage,ChatId,CurrentUpdateId=GetLastMessage()
        if PreviousLastMessage==CurrentLastMessage and CurrentUpdateId==PreviousUpdateId:
            print('continue4')
            continue
        else:
            print("ShowFoodItem:",CurrentLastMessage)
            if(CurrentLastMessage=="MainMenu"):
                main()
            results = IntentModel.predict([bag_of_words(CurrentLastMessage, words)])
            results_index = numpy.argmax(results)
            if(results[0][results_index])>0.8:
                tag = labels[results_index]
            
            if(CurrentLastMessage in ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]):
                tag="Days"
                
            elif(CurrentLastMessage in ["Breakfast","Lunch","Dinner"]):
                tag="MealType"
                
            if(tag=="Days"):
                Day=CurrentLastMessage.capitalize()
                ReplyMessage="Select MealType Type to Show"
                print(ReplyMessage)
                Keyboard={'keyboard': [[{'text':'Breakfast'}],
                                       [{'text':'Lunch'}],
                                       [{'text':'Dinner'}],
                                       [{'text':'MainMenu'}],
                                      ]
                          }
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
            if(tag=="MealType"):
                MealType=CurrentLastMessage
                FoodItem=GetFoodItemData(Day,MealType)
                ReplyMessage=Day+":\n"+MealType+":\n"+FoodItem
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
                #return "FoodItems Shown Success",CurrentLastMessage,ChatId,CurrentUpdateId
        PreviousLastMessage=CurrentLastMessage
        PreviousUpdateId=CurrentUpdateId

def ModifyFoodItems(PreviousLastMessage,ChatId,PreviousUpdateId):
    ReplyMessage="Enter add or delete or edit or interchange food item"    
    print(ReplyMessage)
    Keyboard={'keyboard': [[{'text':'Add FoodItem'}],
                           [{'text':'Delete FoodItem'}],
                           [{'text':'Edit FoodItem'}],
                           [{'text':'MainMenu'}],
                        ]
              }
    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
    AddFoodItemFlag=0
    DeleteFoodItemFlag=0
    ModifyFoodItemFlag=0
    DishTypeFlag=0
    while True:
        TodayDate=datetime.datetime.now()
        CurrentLastMessage,ChatId,CurrentUpdateId=GetLastMessage()
        if PreviousLastMessage==CurrentLastMessage and CurrentUpdateId==PreviousUpdateId:
            print('continue5')
            continue
        else:
            print("ModifyFoodItem:",CurrentLastMessage)
            if(CurrentLastMessage=="MainMenu"):
                main()
            results = IntentModel.predict([bag_of_words(CurrentLastMessage, words)])
            results_index = numpy.argmax(results)
            if(results[0][results_index])>0.8:
                tag = labels[results_index]
            if(CurrentLastMessage in ["Add FoodItem","Delete FoodItem","Edit FoodItem"]):
                tag=CurrentLastMessage
            elif(CurrentLastMessage in ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]):
                tag="Days"
            elif(CurrentLastMessage in ["Breakfast","Lunch","Dinner"]):
                tag="MealType"
            elif(CurrentLastMessage in ["MainDish","Combo1","Combo2","Sidedish1","Sidedish2"]):
                tag="DishType"
            else:
                tag=None
                
            if(tag=="Add FoodItem"):
                AddFoodItemFlag=1
                ReplyMessage="Enter the day"    
                print(ReplyMessage)
                Keyboard=WeekDayKeyBoard()
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                
            if(tag=="Delete FoodItem"):
                DeleteFoodItemFlag=1
                ReplyMessage="Enter the day"    
                print(ReplyMessage)
                Keyboard=WeekDayKeyBoard()
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                
                
            if(tag=="Edit FoodItem"):
                ModifyFoodItemFlag=1
                ReplyMessage="Enter the day"    
                print(ReplyMessage)
                Keyboard=WeekDayKeyBoard()
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                
                
            if(tag=="Days"):
                Day=CurrentLastMessage.capitalize()
                ReplyMessage="Enter the MealType breakfast or lunch or dinner"    
                print(ReplyMessage)
                Keyboard={'keyboard': [[{'text':'Breakfast'}],
                                       [{'text':'Lunch'}],
                                       [{'text':'Dinner'}],
                                       [{'text':'MainMenu'}],
                                      ]
                          }
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
            
            if(tag=="MealType"):
                MealType=CurrentLastMessage
                ReplyMessage="Select Dish Type to Interchange"
                Keyboard={'keyboard': [[{'text':'MainDish'}],
                                       [{'text':'Combo1'}],
                                       [{'text':'Combo2'}],
                                       [{'text':'Sidedish1'}],
                                       [{'text':'Sidedish2'}],
                                       [{'text':'MainMenu'}],
                                      ]
                          }
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
            
            if(tag=="DishType"):
                DishType=CurrentLastMessage
                DishTypeFlag=1
                if(AddFoodItemFlag==1):
                    ReplyMessage="Enter the dish name so i will add to my database"
                    print(ReplyMessage)
                    SendMessage(ChatId,ReplyMessage)
                    PreviousLastMessage=CurrentLastMessage
                    PreviousUpdateId=CurrentUpdateId
                    continue
                if(DeleteFoodItemFlag==1):
                    DishNameList=GetDayList(Day,MealType,DishType)
                    if(DishNameList!=None):
                        ReplyMessage="Select the DishName to be deleted"
                        Keyboard=GetKeyboard(DishNameList)
                        print(ReplyMessage)
                        SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                        PreviousLastMessage=CurrentLastMessage
                        PreviousUpdateId=CurrentUpdateId
                        continue
                    else:
                        ReplyMessage="No data is there to be deleted"
                        print(ReplyMessage)
                        SendMessage(ChatId,ReplyMessage)
                if(ModifyFoodItemFlag==1):
                    DishNameList=GetDayList(Day,MealType,DishType)
                    if(DishNameList!=None):
                        ReplyMessage="Select the DishName to be Modify or edit"
                        Keyboard=GetKeyboard(DishNameList)
                        print(ReplyMessage)
                        SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
                        PreviousLastMessage=CurrentLastMessage
                        PreviousUpdateId=CurrentUpdateId
                        continue
                    else:
                        ReplyMessage="No data is there to edit"
                        print(ReplyMessage)
                        SendMessage(ChatId,ReplyMessage)
                        
            if(AddFoodItemFlag==1 and DishTypeFlag==1):
                AddFoodItem(Day,MealType,DishType,CurrentLastMessage)
                AddFoodItemFlag=0
                RescheduleMealPlan()
                ReplyMessage="Food Item is Added"
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
                return "Modification Success",CurrentLastMessage,ChatId,CurrentUpdateId
            if(DeleteFoodItemFlag==1 and DishTypeFlag==1):
                DeleteFoodItem(Day,MealType,DishType,CurrentLastMessage)
                DeleteFoodItemFlag=0
                RescheduleMealPlan()
                ReplyMessage="Food Item is Deleted"
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
                return "Modification Success",CurrentLastMessage,ChatId,CurrentUpdateId
            if(ModifyFoodItemFlag==1 and DishTypeFlag==1):
                Dish=CurrentLastMessage
                ModifyFoodItemFlag=2
                ReplyMessage="Enter the correct dish name "
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
                PreviousLastMessage=CurrentLastMessage
                PreviousUpdateId=CurrentUpdateId
                continue
                
            if(ModifyFoodItemFlag==2 and DishTypeFlag==1):
                EditFoodItem(Day,MealType,DishType,Dish,CurrentLastMessage)
                DeleteFoodItemFlag=0
                RescheduleMealPlan()
                ReplyMessage="Food Item name is Modified"
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
                return "Modification Success",CurrentLastMessage,ChatId,CurrentUpdateId
       
        PreviousLastMessage=CurrentLastMessage
        PreviousUpdateId=CurrentUpdateId
                
def main():
    PreviousLastMessage,ChatId,PreviousUpdateId=GetLastMessage()
    ReplyMessage="I am your Bot!\nAccording to Now Meal Planning Under Development\nUse the Below Commands to get information from Me"
    print(ReplyMessage)
    Keyboard={'keyboard': [[{'text':'SHOW PLAN'}],
               [{'text':'POSTPOND'}],
               [{'text':'INTERCHANGE'}],
               [{'text':'SHOW FOODITEMS'}],
               [{'text':'EDIT FOODITEMS'}],
              ]
  }
    SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
    while True:
        TodayDate=datetime.datetime.now()
        TodayDateTime=TodayDate.strftime("%H:%M")
        #print(TodayDateTime)
        if(TodayDateTime=="23:00"):
            if(TodayScheduleFlag==1):
                ScheduleForDays(1)
                TodayScheduleFlag=0
        else:
            TodayScheduleFlag=1
            
        CurrentLastMessage,ChatId,CurrentUpdateId=GetLastMessage()
        if PreviousLastMessage==CurrentLastMessage and CurrentUpdateId==PreviousUpdateId:
            print('continue')
            continue
        else:
            print("Main:",CurrentLastMessage)
            if(CurrentLastMessage=="MainMenu"):
                main()
            results = IntentModel.predict([bag_of_words(CurrentLastMessage, words)])
            results_index = numpy.argmax(results)
            if(results[0][results_index])>0.8:
                tag = labels[results_index]
                
            elif(CurrentLastMessage in ['SHOW PLAN','POSTPOND','INTERCHANGE','SHOW FOODITEMS','EDIT FOODITEMS']):
                tag=CurrentLastMessage
            else:
                tag = None
            if(tag==None):
                ReplyMessage="I Couldn't Understand You Say it Again"
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
                pass
            elif (tag=="Greeting") or (CurrentLastMessage=='/start'):
                for tg in Dialogs["intents"]:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                ReplyMessage=random.choice(responses)+"! I am your Bot!\nAccording to Now Meal Planning Under Development\nUse the Below Commands to get information from Me"
                print(ReplyMessage)
                Keyboard={'keyboard': [[{'text':'SHOW PLAN'}],
                                       [{'text':'POSTPOND'}],
                                       [{'text':'INTERCHANGE'}],
                                       [{'text':'SHOW FOODITEMS'}],
                                       [{'text':'EDIT FOODITEMS'}],
                                       [{'text':'MainMenu'}],
                            
                                      ]
              }
                SendMessageWithButtons(ChatId,ReplyMessage,Keyboard)
            if(tag=='SHOW PLAN'):
                Response,CurrentLastMessage,ChatId,CurrentUpdateId=ShowPlan(CurrentLastMessage,ChatId,CurrentUpdateId)
            
            elif(tag=='POSTPOND'):
                Response,CurrentLastMessage,ChatId,CurrentUpdateId=PostpondPlan(CurrentLastMessage,ChatId,CurrentUpdateId)
            
            elif(tag=='INTERCHANGE'):
                Response,CurrentLastMessage,ChatId,CurrentUpdateId=Interchange(CurrentLastMessage,ChatId,CurrentUpdateId)
        
            elif(tag=='SHOW FOODITEMS'):
                Response,CurrentLastMessage,ChatId,CurrentUpdateId=ShowFoodItems(CurrentLastMessage,ChatId,CurrentUpdateId)
                
            elif(tag=='EDIT FOODITEMS'):
                Response,CurrentLastMessage,ChatId,CurrentUpdateId=ModifyFoodItems(CurrentLastMessage,ChatId,CurrentUpdateId)
            
            elif (tag=="Goodbye") or (CurrentLastMessage=='/cancel'):
                for tg in Dialogs["intents"]:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                ReplyMessage=random.choice(responses)+"! I Miss You \n/start-to start chatting with me.\n"
                print(ReplyMessage)
                SendMessage(ChatId,ReplyMessage)
            else:
                for tg in Dialogs["intents"]:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                          
        PreviousLastMessage=CurrentLastMessage
        PreviousUpdateId=CurrentUpdateId
                    
if __name__ == "__main__":
    LoadModelFile()
    main()
