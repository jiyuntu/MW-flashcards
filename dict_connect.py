import json
import re
import requests
import string

API_KEY = "fe536dd4-bcec-4baf-bcd6-0653d25c65e7"

class MerriamWebsterConnect:
    @staticmethod
    def fetch_entry(word):
        url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={API_KEY}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Error: Received status code {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

class MerriamWebsterDict:
    @staticmethod
    def get_audio_url(audio):
        prefix_match = re.search(r'^([0-9]+|gg|bix)', audio)
        if prefix_match:
            prefix = prefix_match.group(1)
            if prefix[0].isdigit() or prefix[0] in string.punctuation:
                prefix = 'number'
        else:
            prefix = audio[0]
        return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{prefix}/{audio}.mp3"

class Headword:
    def __init__(self, data):
        self.__word = self.__remove_non_alphabet(data.get('hwi', {}).get('hw'))
        self.__pos = data.get('fl')
        self.__audio = data.get('hwi', {}).get('prs', [{}])[0].get('sound', {}).get('audio')
        self.__audio_url = MerriamWebsterDict.get_audio_url(self.__audio) if self.__audio else None
        self.__shortdefs = data.get('shortdef')
        self.__example = None

        for definition_block in data.get('def', []):
            for sseq in definition_block.get('sseq', []):
                for sense in sseq:
                    if isinstance(sense, list) and len(sense) > 1:
                        content = sense[1]
                        if isinstance(content, dict) and 'dt' in content:
                            for defining_text in content['dt']:
                                if defining_text[0] == 'vis':
                                    for dt_element in defining_text[1]:
                                        if 't' in dt_element:
                                            example = self.__remove_tokens(dt_element['t'])
                                            self.__example = example
                                            break
                                if self.__example:
                                    break
                    if self.__example:
                        break
                if self.__example:
                    break
            if self.__example:
                break
    @property
    def word(self):
        return self.__word
    @property
    def shortdefs(self):
        return self.__shortdefs
    @property
    def pos(self):
        return self.__pos
    @property
    def example(self):
        return self.__example
    @property
    def audio(self):
        return self.__audio
    @property
    def audio_url(self):
        return self.__audio_url
    @staticmethod
    def __remove_tokens(text):
        return re.sub(r'\{[^}]*\}', '', text)
    @staticmethod
    def __remove_non_alphabet(word):
        regex = re.compile('[^a-zA-Z]')
        return regex.sub('', word)
    def log(self):
        print("-" * 50)
        print(f"WORD:      {self.__word}")
        print(f"POS:       {self.__pos}")
        print(f"Audio URL: {self.__audio_url}")
        print(f"Defs:      {self.__shortdefs}")
        print(f"Example:   {self.__example}")
        print("-" * 50)

class Entry:
    def __init__(self, data, target):
        self.__headwords = []
        for entry in data:
            headword = Headword(entry)
            if headword.word and headword.word.lower() == target.lower():
                self.__headwords.append(headword)
    @property
    def headwords(self):
        return self.__headwords

    def log(self):
        for headword in self.__headwords:
            headword.log()

if __name__ == "__main__":
    target = "bike"
    result = MerriamWebsterConnect.fetch_entry(target)
    entry = Entry(result, target)
    entry.log()
"""
    if result:
        print(json.dumps(result, indent=2))
"""