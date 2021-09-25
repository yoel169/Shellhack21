import logging
import traceback
import json

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
    city_name = get_slot(intent_request,'City')
    hours_type =  get_slot(intent_request,'HoursType')
    day_of_week = get_slot(intent_request,'DayOfWeek')

    reply = ""

    #check if city is correct
    if city_name == storeInfo['address']['city']:
        hour_query = ""

        #reformat input strings
        day_of_week = day_of_week.upper()
        hours_type = hours_type.lower()

        department, hour_query = checkDepartment(hours_type)

        #check for day of week
        for table in storeInfo[hour_query]:
            if day_of_week == table["day"]:
                opening = table["openTime"]
                closing = table["closeTime"]

        reply = """Our {} hours are from {} to {}.
                            """.format(department, opening, closing)

    else:

        reply = """I'm sorry. We currently have no stores in {}.  
        We are currently located at {}.""".format(city_name, storeInfo['address']['city'])

    #reply message
    message =  {
                'contentType': 'PlainText',
                'content': reply
                }
    
    #fulffiled
    fulfillment_state = "Fulfilled"

    return close(intent_request, session_attributes, fulfillment_state, message)


#check for which department
def checkDepartment(hours_type):
    if "sales" in hours_type:
        department = "Sales"
        hour_query = "salesHours"
    elif "service" in hours_type:
        department = "Service"
        hour_query = "serviceHours"
    elif "collision" in hours_type:
        department = "Collision Center"
        hour_query = "collisionHours"

    return department, hour_query

#------------------------ Intents Dispatcher----------------------------------#
def dispatch(intent_request):
    try:
        intent_name = intent_request['sessionState']['intent']['name']

        # Dispatch to your bot's intent handlers
        if intent_name == 'StoreInfo':
            return storeQueryFunction(intent_request)
    
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