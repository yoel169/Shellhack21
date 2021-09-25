import json
import datetime

#import jsons
def importStoreInfo():

    with open('storeinfo.json') as f:
        storeInfo = json.load(f)
    
    with open('customerInfo.json') as a:
        customerdb = json.load(a)

    return (storeInfo, customerdb)

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")

    ### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]

### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


#-------------------------- Super Cool Function starts here ---------------------
# Intents Handlers 
def superCoolFunction(intent_request, storeInfo, customerdb):
    """
    Performs dialog management and fulfillment for selecting a store.
    """
    first_name = get_slots(intent_request)["firstName"]
    last_name = get_slots(intent_request)["lastName"]
    #customer_id = get_slots(intent_request)["id"]

    source = intent_request["invocationSource"]

    #vehicles = get_slots(intent_request)["vehicles"]
    #appointments =get_slots(intent_request)["appointments"]
    #repair_orders = get_slots(intent_request)["repairOrders"]

    if source == "DialogCodeHook":

        #get slots and validate user
        slots = get_slots(intent_request)
        validateUserResult = validateCustomer()

        #if user is not validated
        if not validateUserResult:
            slots[validateUserResult["violatedSlot"]] = None

            # Use the elicitSlot dialog action to re-prompt
            # for the first violation detected.
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validateUserResult["violatedSlot"],
                validateUserResult["message"])


def storeQueryFunction(intent_request, storeInfo):

    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        
        slots = get_slots(intent_request)
        city_name = slots["City"]
        hours_type = slots["HoursType"]
        day_of_week = slots["DayOfWeek"]

        for store in storeInfo:
            if city_name in store["address"]["city"]:
                hour_query = ""
                if "sales" in hours_type:
                    department = "Sales"
                    hour_query = "salesHours"
                elif "service" in hours_type:
                    department = "Service"
                    hour_query = "serviceHours"
                elif "collision" in hours_type:
                    department = "Collision Center"
                    hour_query = "collisionHours"

                for table in store[hour_query]:
                    if day_of_week in table["day"]:
                        opening = table["openTime"]
                        closing = table["closeTime"]

                        return close(
                            intent_request["sessionAttributes"],
                            "Fulfilled",
                            {
                                "contentType": "PlainText",
                                "content": """Our {} hours are from {} to {}.
                                """.format(department, opening, closing)
                            }
                        )
            
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": "There was an error processing your request."
        }
    )


def validateCustomer(name, storedb):

    if name in storedb:
        return True
    else:
        return False


def validateStoreHours(storeInfo):

    if (salesHours in storedb and
        serviceHours in storedb and
        collisionHours in storeDB):
        return True
    else
        return False


#------------------------ Intents Dispatcher----------------------------------#
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    storeInfo, customerdb = importStoreInfo()
    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "AutoNationResponse":
        return superCoolFunction(intent_request, storeInfo, customerdb)
    if intent_name == "StoreInfo":
        return storeQueryFunction(intent_request, storeInfo)

    raise Exception("Intent with name " + intent_name + " not supported")


# ------------------------------main lambda handler-------------------------------
def lambda_handler(event, context):
   """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    return dispatch(event)

"""
def timeCalculator(opening, closing):

    current_time = datetime.now()
    open_time = current_time
    open_time.hour = opening.split(":")[0]
    open_time.minute = opening.split(":")[1]
    close_time = current_time
    close_time.hour = closing.split(":")[0]
    close_time.minute = closing.split(":")[1]

    if current_time > open_time and current_time < close_time:
        return True
    else
        return False
"""


def __init__():
    importStoreInfo()
