from Shellhack21.customer_logic import customerQueryFunction
import logging
import traceback
import json
from datetime import datetime

debug=True

#import json
def importJSON(which):

    if which == 'store':
        with open('storeinfo.json') as f:
            info = json.load(f)

    else:
        with open('customerInfo.json') as a:
            info = json.load(a)
    
    return info

#store query
def storeQueryFunction(intent_request):

    #import store info
    storeInfo = importJSON('store')

    #get session attributes
    session_attributes = get_session_attributes(intent_request)

    #get slot values
    #city_name = get_slot(intent_request,'City')
    department =  get_slot(intent_request,'Department')
    day_of_week = get_slot(intent_request,'DayOfWeek')

    #reformat input strings
    day_of_week = day_of_week.upper()
    department = department.lower()

    #check for store hours based on client input
    storeHours = checkStoreInfo(day_of_week, department, storeInfo)

    #insert store hours
    message =  {
                'contentType': 'PlainText',
                'content': storeHours
                }
    
    #fulffiled
    fulfillment_state = "Fulfilled"

    #return reply
    return close(intent_request, session_attributes, fulfillment_state, message)

#check for store hours
def checkStoreInfo(day, dep, storeInfo):

    #check which department
    if "sales" in dep:
        department = "Sales"
        dep_query = "salesHours"
    elif "service" in dep:
        department = "Service"
        dep_query = "serviceHours"
    elif "collision" in dep:
        department = "Collision Center"
        dep_query = "collisionHours"
    else:
        return "Could not find that department. Our departments are: Sales, Service, and Collision."

    #check if user actually checked for a possible day
    possibleDays = ['MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY','WEEKDAY','WEEKEND'] 
    if not day in possibleDays:
        return "Can not find hours for {}.".format(day)

    #check if user is asking for weekday
    if day == "WEEKDAY":
        hoursString = ""
        for table in storeInfo[dep_query]:
            opening = table["openTime"]
            closing = table["closeTime"]

            hoursString += "{}: from {} to {}.\n\n".format(table["day"],reformatTime(opening), reformatTime(closing))

        return "Our {} is open on: \n {}".format(department, hoursString)

    #check if user asked for weekend hours
    elif day == "WEEKEND":
        
        salBool = False
        sunBool = False

        for table in storeInfo[dep_query][5:]:
            
            #check if department is open saturday
            if table["day"] == "SATURDAY":
              
                satOpen = reformatTime(table["openTime"])
                satClose = reformatTime(table["closeTime"])
                salBool = True

             #check if department is open sunday
            if  table["day"] == "SUNDAY":
              
                sunOpen = reformatTime(table["openTime"])
                sunClose = reformatTime(table["closeTime"])
                sunBool = True
        
        if salBool and sunBool:
            return "Our {} is open on Saturday from {} to {} and on Sunday from {} to {}.".format(department, satOpen, satClose, sunOpen, sunClose)
        elif salBool:
            return "Our {} is open on Saturday from {} to {} and closed on Sunday.".format(department, satOpen, satClose)
        else:
            return "Our {} is closed on Saturday and Sunday.".format(department)
    
    #check for a specific day
    for table in storeInfo[dep_query]:
        if day == table["day"]:
            opening = table["openTime"]
            closing = table["closeTime"]

            return "Our {} hours are from {} to {}.".format(department, reformatTime(opening), reformatTime(closing))

    return "Our {} is closed on {}.".format(department, (day[:1] + day[1:].lower()))

def reformatTime(time):
    return datetime.strptime(time, "%H:%M").strftime("%I:%M %p")

#------------------------ Intents Dispatcher----------------------------------#
def dispatch(intent_request):
    try:
        intent_name = intent_request['sessionState']['intent']['name']

        # Dispatch to your bot's intent handlers
        if intent_name == 'StoreInfo':
            return storeQueryFunction(intent_request)
        elif intent_name == 'CustomerInfo':
            return customerQueryFunction(intent_request)
    
    except Exception as ex:
        error = traceback.format_exc()
        print(error)
        return fail(intent_request,error)


#entry point of lambda
def lambda_handler(event, context):
    response = dispatch(event)
    return response

# builds response to end the dialog
def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }   
# on error, return nice message to bot
def fail(intent_request,error):
    #don't share the full eerror in production code, it's not good to give full traceback data to users
    error = error if debug else ''
    intent_name = intent_request['sessionState']['intent']['name']
    message = {
                'contentType': 'PlainText',
                'content': f"Oops... I guess I ran into an error I wasn't expecting... Sorry about that. My dev should probably look in the logs.\n {error}"
                }
    fulfillment_state = "Fulfilled"
    return close(intent_request, get_session_attributes(intent_request), fulfillment_state, message) 

#gets a map of the session attributes
def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}

#util method to get the slots fromt he request
def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']

#util method to get a slot's value
def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None and 'interpretedValue' in slots[slotName]['value']:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None

# builds response to tell the bot you want to trigger another intent (use to switch the context)
def elicit_intent(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [ message ] if message != None else None,
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }

# builds response to tell the bot you need to get the value of a particular slot
def elicit_slot(intent_request, session_attributes,slot_to_elicit, message):
    intent_request['sessionState']['intent']['state'] = 'InProgress'
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }