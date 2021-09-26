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

def customerQueryFunction(intent_request):
    
    storeInfo = importJSON("store")
    customerInfo = importJSON("customer")

    session_attributes = get_session_attributes(intent_request)

    slots = get_slots(intent_request)

    first_name = slots["firstName"]
    last_name = slots["lastName"]

    first_name_found = False
    matches = []

    for customer in customerInfo:
        if first_name == customer["firstName"]:
            matches.add(customer)
            first_name_found = True
            break

    if not first_name_found:
        return elicit_slot(
                intent_request,
                get_session_attributes(intent_request),
                "firstName",
                "Your first name was not in our database."
        )

    last_name_found = False
    
    for customer in matches:
        if last_name == customer["lastName"]:
            current_customer = customer
            customer_ID = customer["customerID"]
            last_name_found = True
            break

    if not last_name_found:
        return elicit_slot(
                intent_request,
                get_session_attributes(intent_request),
                "lastName",
                "Your last name was not in our database."
        )

    query_type = slots["queryType"]
    make = slots["carMake"]
    model = slots["carModel"]
    vin = getVIN(current_customer, make, model)

    if query_type == "appointment":
        message = checkRepairStatus(current_customer, vin)
    elif query_type == "repair":
        message = checkRepairStatus(current_customer, vin)
    else:
        #Edge case fails
        return fail(intent_request, "Invalid query type")
    return close(
        intent_request,
        session_attributes,
        "Completed",
        message
    )



#Take a customer ID from the intent_request
def getCustomerID(intent_request):

    session_attributes = get_session_attributes(intent_request)

    slots = get_slots(intent_request)
    first_name = slots["firstName"]
    last_name = slots["lastName"]

    first_name_found = False
    matches = []

    for customer in customerInfo:
        if first_name == customer["firstName"]:
            matches.add(customer)
            first_name_found = True

    if not first_name_found:
        elicit_slot(
                intent_request,
                get_session_attributes(intent_request),
                "firstName",
                "Your first name was not in our database."
        )
    
    for customer in matches:
        if last_name == customer["lastName"]:
            return customer_ID

    elicit_slot(
            intent_request,
            get_session_attributes(intent_request),
            "lastName",
            "Your last name was not in our database."
    )

#Given a customer and VIN, check if any repairs are ready.
def checkRepairStatus(customer, vin):

    for order in customer["repairOrders"]:
        if vin == order["vehicleID"]:
            if order["status"] == "COMPLETED":
                message = "Your repair for your {} has been completed".format(
                    getCarInfo(vin)
                )
            elif order["status"] == "OPEN":
                message =  "Your repair for your {} is currently in progress".format(
                    getCarInfo(vin)
                )

    return "No current repairs could be found for your {}".format(
        getCarInfo(vin)
    )

#Given a customer and car, check if said car has any upcoming appointments
def checkAppointmentStatus(customer, vin):

    appointment_list = []
    appointment_count = 0

    current_time = datetime.utcnow()

    for appointment in customer["appointments"]:
        if appointment["vehicleID"] == vin
        appointment_time = readTime(appointment["appointmentDateTime"])
        if current_time < appointment_time:
            appointment_list.add("Appointment on {1:%B} {1:%d} at {1:%I}:{1:%M} {1:%p}.\n".format(
                getCarInfo(vin),
                appointment_time
            ))
            appointment_count += 1

    if appointment_count > 0:
        response_string = "You have {0} upcoming appointments:\n"
        for appointment in appointment_list:
            response_string.append(appointment)
        return response_string
    else:
        return "No appointments could be found."


#------------------------ Intents Dispatcher----------------------------------#
def dispatch(intent_request):
    try:
        intent_name = intent_request['sessionState']['intent']['name']

        # Dispatch to your bot's intent handlers
        if intent_name == 'StoreInfo':
            return storeQueryFunction(intent_request)
        elif intent_name == 'CustomerInfo':
            return "Function name here"
    
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