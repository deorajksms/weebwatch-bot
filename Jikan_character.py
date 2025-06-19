import requests

def fetch_character(query):
    url = f"https://api.jikan.moe/v4/characters?q={query}&limit=1"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            character = data['data'][0]
            print("\n✅ Character Found!")
            print(f"Name     : {character['name']}")
            print(f"About    : {character.get('about', 'No bio available.')[:300]}...")
            print(f"Image    : {character['images']['jpg']['image_url']}")
            print(f"URL      : {character['url']}")
        else:
            print("❌ No results found. Try another name.")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error: {http_err}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Check your internet or firewall.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Try again.")
    except requests.exceptions.RequestException as err:
        print(f"❌ Unexpected error: {err}")

if __name__ == "__main__":
    query = input("🔎 Enter character name: ").strip()
    if query:
        fetch_character(query)
    else:
        print("❗ Query cannot be empty.")
