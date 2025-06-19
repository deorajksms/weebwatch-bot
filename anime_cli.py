import requests

def search_jikan(content_type: str, query: str):
    url = f"https://api.jikan.moe/v4/{content_type}?q={query}&limit=5"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and data['data']:
            print(f"\n🔎 Top results for {content_type.title()} '{query}':\n")
            for i, item in enumerate(data['data'], 1):
                title = item.get('title') or item.get('name')
                synopsis = item.get('synopsis') or item.get('about', 'No description available.')
                score = item.get('score', 'N/A')
                url = item['url']
                print(f"{i}. 📚 Title: {title}")
                print(f"   ⭐ Score: {score}")
                print(f"   📝 Info: {synopsis[:200]}...")
                print(f"   🔗 URL: {url}\n")
        else:
            print("❌ No results found.")

    except requests.exceptions.RequestException as e:
        print("❌ Network/API Error:", e)


def main():
    print("🎌 Welcome to Anime/Manga Search CLI")
    print("Choose search type:\n1. Anime\n2. Manga\n3. Character")
    choice = input("Enter choice (1/2/3): ")

    content_type = {"1": "anime", "2": "manga", "3": "characters"}.get(choice)
    if not content_type:
        print("❗ Invalid choice.")
        return

    query = input(f"🔎 Enter {content_type.title()} title: ")
    search_jikan(content_type, query)


if __name__ == '__main__':
    main()
