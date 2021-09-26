from customer_logic import customerQueryFunction, customerAppointmentFactory
from storeInfo import storeInfoQueryFunction
import traceback
from storeHours import storeQueryFunction
from lambdaUtilityFunctions import fail

#THIS WAS MADE FOR AWS LEX V2. IS NOT COMPATIBLE WITH LEX V1
#BY YOEL ROBAINA, MAURICIO SILVA, JONATHAN MONTESINOS, JORDAN X

def dispatch(intent_request):
    try:
        intent_name = intent_request['sessionState']['intent']['name']

        # Dispatch to your bot's intent handlers
        if intent_name == 'StoreHours':
            return storeQueryFunction(intent_request)
        elif intent_name == 'CustomerInfo':
             return customerQueryFunction(intent_request)
        elif intent_name == 'StoreInfo':
             return storeInfoQueryFunction(intent_request)
        elif intent_name == 'MakeAppointment':
            return  customerAppointmentFactory(intent_request)
            
    except Exception as ex:
        error = traceback.format_exc()
        print(error)
        return fail(intent_request,error)


#entry point of lambda
def lambda_handler(event, context):
    response = dispatch(event)
    return response