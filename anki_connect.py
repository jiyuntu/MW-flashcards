import json
import urllib.request

class AudioFile:
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename

class PictureFile:
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename

class AnkiConnect:
    @staticmethod
    def make_payload(action, **params):
        return {'action': action, 'params': params, 'version': 6}

    @staticmethod
    def invoke(action, **params):
        payload = AnkiConnect.make_payload(action, **params)
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

class AddNoteAction:
    @staticmethod
    def format_params(front, back, audio_file: AudioFile = None, picture_file: PictureFile = None):
        """
        Formats the parameters for the 'addNote' action.
        """
        ret = {
            "note": {
                "deckName": "Merriam Webster",
                "modelName": "Basic",
                "fields": {
                    "Front": front,
                    "Back": back
                },
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                    "duplicateScopeOptions": {
                        "deckName": "Merriam Webster",
                        "checkChildren": False,
                        "checkAllModels": False
                    }
                },
            }
        }
        if audio_file:
            ret["note"]["audio"] = [{
                "url": audio_file.url,
                "filename": audio_file.filename,
                "fields": ["Front"]
            }]
        if picture_file:
            ret["note"]["picture"] = [{
                "path": picture_file.path,
                "filename": picture_file.filename,
                "fields": ["Back"]
            }]
        return ret

if __name__ == "__main__":
    front = "猫"
    back = "ねこ (Cat)"
    url = "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=猫&kana=ねこ"
    filename = "yomichan_ねこ_猫.mp3"
    note_params = AddNoteAction.format_params(front, back, url, filename)
    try:
        result = AnkiConnect.invoke('addNote', **note_params)
        print(f"Successfully added note with ID: {result}")
    except Exception as e:
        print(f"Error: {e}")