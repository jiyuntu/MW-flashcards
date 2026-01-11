import requests
import json

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

if __name__ == "__main__":
    result = MerriamWebsterConnect.fetch_entry("python")
    if result:
        print(json.dumps(result, indent=2))