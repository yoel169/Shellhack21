from lambdaUtilityFunctions import close,get_slot,get_session_attributes, importJSON
from emojiesUnicode import getEmojie

def storeInfoQueryFunction(intent_request):

    #get query type
    storeQuery = get_slot(intent_request,'storeInfoQuery')

    #get session attributes
    session_attributes = get_session_attributes(intent_request)

    #get store info
    storeInfo = getStoreInfo(storeQuery)

    #insert store info string
    message =  {
                'contentType': 'PlainText',
                'content': storeInfo
                }
    
    #fulffiled
    fulfillment_state = "Fulfilled"

    #return reply
    return close(intent_request, session_attributes, fulfillment_state, message)


def getStoreInfo(queryT):
    #import store info
    storeInfo = importJSON('store')
    
    #get store info
    info = storeInfo[queryT]

    response = getEmojie('penguin') + " "

    #check if info is a dictionary
    if(type(info) == dict):

        if queryT == 'address':
            response += getEmojie('card') + " "
        else:
            response += getEmojie('watch') + " "

        for key, value in info.items():
            response+= "{}: {}, \n".format(key, value)

    elif(type(info) == list):
        for value in info:
            response+= "{},".format(value)

    else:
        if queryT == 'faxNumber':
            response += getEmojie('fax') + " "
        elif queryT == 'phoneNumber' or  queryT =='servicephoneNumber':
             response += getEmojie('phone') + " "
        elif queryT == 'webAddress':
            response += getEmojie('globe') + " "

        response += "{} is {}".format(queryT, info)
    
    return response

