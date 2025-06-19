import httpx

try:
    r = httpx.get("https://api.jikan.moe/v4/anime?q=Naruto", timeout=10)
    print("✅ Connected:", r.status_code)
    print("Response:", r.json())
except Exception as e:
    print("❌ Connection failed:", e)
