import datetime
import re
from lambdaUtilityFunctions import close,get_slot,get_session_attributes, importJSON

def customerQueryFunction(intent_request):
    
    storeInfo = importJSON("store")
    customerInfo = importJSON("customer")

    session_attributes = get_session_attributes(intent_request)

    first_name = get_slot(intent_request, "firstName")
    last_name = get_slot(intent_request, "lastName")

    first_name_found = False
    last_name_found = False
    matches = []

    #for customer in customerInfo:
    if first_name.lower() == customerInfo["firstName"].lower():
        matches.append(first_name)
        first_name_found = True
        
    if not first_name_found:

        reply = "Your first name was not in our database."
        message =  {
                    'contentType': 'PlainText',
                    'content': reply
                    }

        return close(intent_request,session_attributes,"Fulfilled",message)
  
    #for customer in matches:
    if last_name.lower() == customerInfo["lastName"].lower():
        current_customer = customerInfo
        last_name_found = True
    

    if not last_name_found:

        reply = "Your last name was not in our database."
        message =  {
                    'contentType': 'PlainText',
                    'content': reply
                    }

        return close(intent_request,session_attributes,"Fulfilled",message)


    make = get_slot(intent_request,"carMake")
    model = get_slot(intent_request,"carModel")
    query_type = get_slot(intent_request,"queryType")
    vin = getVIN(current_customer, make, model)

    #checking if a car was found
    if vin == "not found":

        reply = "There was no car found for {} {}.".format(make, model)
        message =  {
                    'contentType': 'PlainText',
                    'content': reply
                    }

        return close(intent_request,session_attributes,"Fulfilled",message)

    else:

        if query_type == "appointment":
            reply = checkAppointmentStatus(current_customer, vin)
        elif query_type == "repair":
            reply = checkRepairStatus(current_customer, vin)
        else:
            #Edge case fails
            return fail(intent_request, "Invalid query type")

        #message to close intent
        message =  {
                    'contentType': 'PlainText',
                    'content': reply
                    }

    return close(
        intent_request,
        session_attributes,
        "Fulfilled",
        message
    )


#Given a customer, and their car's make and model
#find the VIN
def getVIN(customer, make, model):
    
    if model == 'grandcherokee': model = 'grand cherokee'

    for vehicle in customer["vehicles"]:
        if make.lower() == vehicle["make"].lower() and model.lower() == vehicle["model"].lower():
            return vehicle["vehicleId"]

    return "not found"


#Take a customer ID from the intent_request
# def getCustomerID(intent_request):

#     session_attributes = get_session_attributes(intent_request)

#     slots = get_slots(intent_request)
#     first_name = slots["firstName"]
#     last_name = slots["lastName"]

#     first_name_found = False
#     matches = []

#     #for customer in customerInfo:
#         if first_name == customer["firstName"]:
#             matches.append(customer)
#             first_name_found = True

#     if not first_name_found:

#         #insert store hours
#         message =  {
#                 'contentType': 'PlainText',
#                 'content': "Your first name was not in our database."
#                 }

#         return elicit_slot(
#                 intent_request,
#                 get_session_attributes(intent_request),
#                 "firstName", message
                
#         )
    
#     for customer in matches:
#         if last_name == customer["lastName"]:
#             return customer_ID

#     return elicit_slot(
#             intent_request,
#             get_session_attributes(intent_request),
#             "lastName",
#             "Your last name was not in our database."
#     )

#Given a VIN, look up the make and model
def getCarInfo(vin, customer):

    #for customer in customerInfo:
    for vehicle in customer["vehicles"]:
        if vin == vehicle["vehicleId"]:
            return "{} {} {}".format(
                vehicle["year"],
                vehicle["make"],
                vehicle["model"]
            )

    return ""

#Given a customer and VIN, check if any repairs are ready.
def checkRepairStatus(customer, vin):

    for order in customer["repairOrders"]:
        if vin == order["vehicleId"]:
            if order["status"] == "COMPLETED":
                return "Your repair for your {} has been completed".format(
                    getCarInfo(vin, customer)
                )
            elif order["status"] == "OPEN":
                return "Your repair for your {} is currently in progress".format(
                    getCarInfo(vin, customer)
                )

    return "No current repairs could be found for your {}".format(
        getCarInfo(vin, customer)
    )


#Given a customer and car, check if said car has any upcoming appointments
def checkAppointmentStatus(customer, vin):

    appointment_list = []
    appointment_count = 0

    #current_time = datetime.datetime.utcnow()

    for appointment in customer["appointments"]:
        if appointment["vehicleId"] == vin:

            #appointment_time = readTime(int(appointment["appointmentDateTime"]))

            appointment_time = appointment["appointmentDateTime"]

            #if current_time < appointment_time:
            appointment_list.append("Appointment on vehicle '{}' at {}.\n".format(
                getCarInfo(vin, customer),
                appointment_time
            ))
            appointment_count += 1

    if appointment_count > 0:
        response_string = "You have {0} upcoming appointments:\n".format(appointment_count)
        for appointment in appointment_list:
            response_string += appointment
        return response_string
    else:
        return "No appointments could be found."

#Converts ISO time string to datetime object
def readTime(time_string):

    buffer = re.split("-:TZ", str(time_string))
    year = int(buffer[0])
    month = int(buffer[1])
    day = int(buffer[2])
    hour = int(buffer[3])
    minute = int(buffer[4])
    second = int(buffer[5])

    datetime_obj = datetime.datetime(year, month, day, hour, minute, second)

    return datetime_obj
