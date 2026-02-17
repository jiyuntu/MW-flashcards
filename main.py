import sys
import vlc
from dict_connect import MerriamWebsterConnect, Entry
from anki_connect import AnkiConnect, AddNoteAction

class MWAnkiCard:
    def __init__(self, entry: Entry):
        self.__front = entry.headwords[0].word
        definitions = [(headword.pos, "; ".join(headword.shortdefs)) for headword in entry.headwords]
        self.__back = "<br>".join(f"[{definition[0]}] {definition[1]}" for definition in definitions)
        # MW sorts usage (headwords) based on frequency. Take the first
        # example and audio url as they might be the most common.
        example = next((headword.example for headword in entry.headwords if headword.example), None)
        if example:
            self.__back += f"<br>{example}"
        self.__audio, self.__audio_url = next(
            ((headword.audio, headword.audio_url) for headword in entry.headwords if headword.audio_url),
            (None, None))
    @property
    def front(self):
        return self.__front
    @property
    def back(self):
        return self.__back
    @property
    def audio(self):
        return self.__audio
    @property
    def audio_url(self):
        return self.__audio_url

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
        p = vlc.MediaPlayer(card.audio_url)
        p.play()
        try:
            params = AddNoteAction.format_params(
                front=card.front,
                back=card.back,
                audio_url=card.audio_url,
                audio_filename=f"{card.audio}.mp3"
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