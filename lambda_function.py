import json

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
    Performs dialog management and fulfillment for recommending a portfolio.
    """
    first_name = get_slots(intent_request)["firstName"]
    last_name = get_slots(intent_request)["lastName"]
    #customer_id = get_slots(intent_request)["id"]

    source = intent_request["invocationSource"]

    #vehicles = get_slots(intent_request)["vehicles"]
    #appointments =get_slots(intent_request)["appointments"]
    #rapir_orders = get_slots(intent_request)["repairOrders"]

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


def validateCustomer(name, storedb):

    if name in storedb:
        return True
    else:
        return False


def validateStoreHours(storeInfo):
    return True


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

    raise Exception("Intent with name " + intent_name + " not supported")


# ------------------------------main lambda handler-------------------------------
def lambda_handler(event, context):
   """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    return dispatch(event)