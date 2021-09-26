import json
import datetime
import dateutil
import re

customerInfo = {}

def importJSON():

    with f as open("customerInfo.json"):
        customerInfo = json.read(f)

"""
def storeAddress(store):

    address = store["address"]

    return {}
    {}
    {}
    {}, {} {}.format(store["name"],
        address["street1"],
        address["street2"],
        address["city"],
        address["state"],
        address["zip"]
    )


def customerQuery(intent_request):

    session_attributes = get_session_attributes(intent_request)
"""

#Take a customer ID from the intent_request
def getCustomerID(intent_request):

    session_attributes = get_session_attributes(intent_request)

    slots = get_slots(intent_request)
    first_name = slots["firstName"]
    last_name = slots["lastName"]

    for customer in customerInfo:
        if first_name == customer["firstName"] and last_name == customer["lastName"]:
            return customer["customerId"]
    
    return null


#Given a VIN, look up the make and model
def getCarInfo(vin):

    for customer in customerInfo:
        for vehicle in customer["vehicles"]:
            if vin == vehicle["vehicleID"]:
                return "{} {} {}".format(
                    vehicle["year"],
                    vehicle["make"],
                    vehicle["model"]
                )

    return None

#Given a customer, and their car's make and model
#find the VIN
def getVIN(customer, make, model):

    for vehicle in customer["vehicles"]:
        if make.lower() == vehicle["make"].lower() and model.lower() == vehicle["model"].lower():
            return vehicle["vehicleID"]

    return None


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

        
#Alias for dateutil.parser.isoparse()
def readTime(time_string):

    return dateutil.parser.isoparse(time_string)

    """
    buffer = re.split("-:TZ", time_string)
    year = int(buffer[0])
    month = int(buffer[1])
    day = int(buffer[2])
    hour = int(buffer[3])
    minute = int(buffer[4])
    second = int(buffer[5])

    datetime_obj = datetime.datetime(year, month, day, hour, minute, second)

    return datetime_obj
    """

#Given a customer and VIN, check if any repairs are ready.
def checkRepairStatus(customer, vin):

    for order in customer["repairOrders"]:
        if vin == order["vehicleID"]:
            if order["status"] == "COMPLETED":
                return "Your repair for your {} has been completed".format(
                    getCarInfo(vin)
                )
            elif order["status"] == "OPEN":
                return "Your repair for your {} is currently in progress".format(
                    getCarInfo(vin)
                )

    return "No current repairs could be found for your {}".format(
        getCarInfo(vin)
    )

