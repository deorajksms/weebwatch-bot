import requests

def fetch_anime(query):
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"

    try:
        response = requests.get(url, timeout=10)  # 10-second timeout
        response.raise_for_status()  # Raise error for HTTP status codes like 404, 500

        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            anime = data['data'][0]
            print("\n✅ Anime Found!")
            print(f"Title     : {anime['title']}")
            print(f"Episodes  : {anime.get('episodes', 'Unknown')}")
            print(f"Score     : {anime.get('score', 'N/A')}")
            print(f"Synopsis  : {anime.get('synopsis', 'No synopsis.')[:300]}...")
            print(f"URL       : {anime['url']}")
        else:
            print("❌ No results found. Try a different title.")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error: {http_err}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Check your internet or firewall.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Try again.")
    except requests.exceptions.RequestException as err:
        print(f"❌ Unexpected error: {err}")

if __name__ == "__main__":
    query = input("🔎 Enter anime title: ").strip()
    if query:
        fetch_anime(query)
    else:
        print("❗ Query cannot be empty.")
