import os
import sys
import vlc
from dict_connect import MerriamWebsterConnect, Entry
from anki_connect import AnkiConnect, AddNoteAction, AudioFile, PictureFile

class MWAnkiCard:
    def __init__(self, entry: Entry):
        self.__front = entry.headwords[0].word
        definitions = [(headword.pos, "; ".join(headword.shortdefs)) for headword in entry.headwords]
        self.__base_back = "<br>".join(f"[{definition[0]}] {definition[1]}" for definition in definitions)
        # MW sorts usage (headwords) based on frequency. Take the first
        # example and audio url as they might be the most common.
        self.__example = next((headword.example for headword in entry.headwords if headword.example), None)
        self.__audio, self.__audio_url = next(
            ((headword.audio, headword.audio_url) for headword in entry.headwords if headword.audio_url),
            (None, None))
        self.__custom_example = None
        self.__picture = None
        self.__picture_path = None
    @property
    def front(self):
        return self.__front
    @property
    def back(self):
        content = [self.__base_back]
        if self.__example:
            content.append(f"<br><br>{self.__example}")
        if self.__custom_example:
            content.append(f"<br><br>{self.__custom_example}")
        if self.__picture:
            content.append("<br>")
        return "".join(content)
    @property
    def audio(self):
        return self.__audio
    @property
    def audio_url(self):
        return self.__audio_url
    @property
    def picture(self):
        return self.__picture
    @property
    def picture_path(self):
        return self.__picture_path
    def add_example_sentence(self, sentence):
        self.__custom_example = sentence
    def add_picture(self, picture):
        self.__picture = picture
        self.__picture_path = os.path.abspath(f"data/{picture}")

def add(target):
    data = MerriamWebsterConnect.fetch_entry(target)
    if not data:
        print(f"No results found for '{target}'.")
        return

    entry = Entry(data)
    if entry.count(target) > 0:
        entry.filter(target)
        entry.log()
        card = MWAnkiCard(entry)
        if card.audio_url:
            p = vlc.MediaPlayer(card.audio_url)
            p.play()
        example_sentence = input("Enter an example sentence: ").strip()
        if example_sentence:
            card.add_example_sentence(example_sentence)
        picture = input("Enter a picture filename (in data/): ").strip()
        if picture:
            card.add_picture(picture)
        try:
            params = AddNoteAction.format_params(
                front=card.front,
                back=card.back,
                audio_file=AudioFile(url=card.audio_url, filename=f"{card.audio}.mp3") if card.audio_url else None,
                picture_file=PictureFile(path=card.picture_path, filename=card.picture) if card.picture else None
            )
            note_id = AnkiConnect.invoke('addNote', **params)
            print(f"✅ Added to Anki (ID: {note_id})")
        except Exception as e:
            print(f"❌ Anki Error: {e}")
    else:
        print(f"No entry found for {target}.")
        for headword in entry.headwords:
            response = input(f"Would you like to add {headword.word} instead? (yes/no): ")
            response = response.strip().lower()
            if response == "yes":
                add(headword.word)
                return

def main():
    try:
        while True:
            target = input("Enter word to look up: ").strip()
            if not target:
                continue
            add(target)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()