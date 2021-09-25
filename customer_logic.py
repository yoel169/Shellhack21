import json
import datetime

customerInfo = {}

def importJSON():

    with f as open("customerInfo.json"):
        customerInfo = json.read(f)


def storeName(store):
    return store["name"]

def storeAddress(store):

    address = store["address"]

    return """{}
    {}
    {}
    {}, {} {}""".format(store["name"],
        address["street1"],
        address["street2"],
        address["city"],
        address["state"],
        address["zip"]
    )

"""
def customerQuery(intent_request):

    session_attributes = get_session_attributes(intent_request)
"""


def getCustomerID(intent_request):

    session_attributes = get_session_attributes(intent_request)

    slots = get_slots(intent_request)
    first_name = slots["firstName"]
    last_name = slots["lastName"]

    for customer in customerInfo:
        if first_name == customer["firstName"] and last_name == customer["lastName"]:
            return customer["customerId"]
    
    return null

def getCarInfo(vin):

    for customer in customerInfo:
        for vehicle in customer["vehicles"]:
            if vin == vehicle["vehicleID"]:
                return "{} {} {}".format(
                    vehicle["year"],
                    vehicle["make"],
                    vehicle["model"]
                )

    return null

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

    return "No repairs could be found for your {}".format(
        getCarInfo(vin)
    )

