import requests

HEADERS = {'Content-Type': 'application/json'}


def db_record(event, context):
    try:
        for record in event.get('Records'):
            if record.get('eventName') != 'MODIFY':
                continue

            newImage = record.get('dynamodb').get('NewImage')

            labels_record = newImage.get('labels')

            if not labels_record:
                continue

            labels = labels_record.get('S')
            callback_url = newImage.get('callback_url').get('S')

            requests.post(url=callback_url, data=labels, headers=HEADERS)
    except Exception as e:
        return e
