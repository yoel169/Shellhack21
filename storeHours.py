from lambdaUtilityFunctions import close,get_slot,get_session_attributes, importJSON
from datetime import datetime

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