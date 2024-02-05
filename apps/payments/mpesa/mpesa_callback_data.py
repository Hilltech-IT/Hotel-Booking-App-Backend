from apps.payments.models import MpesaResponseData


def mpesa_callback_data_distructure(data):
    try:
        callback_data = data['Body']['stkCallback']

        result_description = callback_data.get("ResultDesc")
        response_code = callback_data.get("ResultCode")

        if result_description == 'The service request is processed successfully.':
            callback_object = {
                "MerchantRequestID": callback_data.get("MerchantRequestID"),
                "CheckoutRequestID": callback_data.get("CheckoutRequestID"),
                "ResultCode": callback_data.get("ResultCode"),
                "ResultDesc": callback_data.get("ResultDesc"),
                "Amount": [x["Value"] for x in callback_data["CallbackMetadata"]["Item"] if x['Name'] == "Amount"][0],
                "TransactionTimeStamp":  [x["Value"] for x in callback_data["CallbackMetadata"]["Item"] if x['Name'] == "TransactionDate"][0],
                "PhoneNumber":  [x["Value"] for x in callback_data["CallbackMetadata"]["Item"] if x['Name'] == "PhoneNumber"][0],
                "MpesaReceiptNumber":  [x["Value"] for x in callback_data["CallbackMetadata"]["Item"] if x['Name'] == "MpesaReceiptNumber"][0],
            }
            MpesaResponseData.objects.create(response_data=callback_object, response_description=result_description, response_code=response_code)
            return callback_object
        elif result_description == 'The initiator information is invalid.':
            MpesaResponseData.objects.create(response_data=callback_data, response_description=result_description, response_code=response_code)
            return None
    except Exception as e:
        raise e