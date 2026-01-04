import json
import urllib.request

class AnkiConnect:
    @staticmethod
    def request(action, **params):
        return {'action': action, 'params': params, 'version': 6}

    @staticmethod
    def invoke(action, **params):
        payload = AnkiConnect.request(action, **params)
        requestJson = json.dumps(payload).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']

result = AnkiConnect.invoke('deckNames')
print('got list of decks: {}'.format(result))