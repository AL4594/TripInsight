import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import quote

# Load API key from .env
load_dotenv()
PEXELS_KEY = os.getenv("PEXELS_KEY")

# Prepare headers for requests
headers = {
    "Authorization": PEXELS_KEY
}

# Load your list of cities
df = pd.read_csv("./city_data.csv")
cities = df['city']

# Output folder
output_dir = "../static/images"
os.makedirs(output_dir, exist_ok=True)

# Track how many we've downloaded this run
downloaded = 0
MAX_PER_RUN = 180

# Start processing
for city in cities:
    # Format safe filename
    safe_name = city.replace('/', '_').strip()
    file_path = os.path.join(output_dir, f"{safe_name}.jpg")

    # Skip if already exists
    if os.path.exists(file_path):
        continue

    print(f"Searching for: {city}")
    try:
        query = quote(city)
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=5"
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            print("Rate limit hit! Sleeping 60 minutes...")
            time.sleep(3600)
            continue
        elif response.status_code != 200:
            print(f"Error {response.status_code} for {city}")
            continue

        data = response.json()
        photos = data.get("photos", [])

        # Find first non-AI image
        image_url = None
        for photo in photos:
            if not photo.get("ai_generated", False):
                image_url = photo["src"]["original"]
                break

        if image_url:
            img_data = requests.get(image_url).content
            with open(file_path, 'wb') as f:
                f.write(img_data)
            print(f"✅ Saved: {file_path}")
            downloaded += 1
        else:
            print(f"⚠️ No non-AI photo found for {city}")

        # Check remaining quota
        remaining = response.headers.get("X-Ratelimit-Remaining")
        print(f"Remaining quota: {remaining}")

        # Stop if we reach per-run cap
        if downloaded >= MAX_PER_RUN:
            print(f"🛑 Reached {MAX_PER_RUN} images. Run this script again to continue.")
            break

    except Exception as e:
        print(f"❌ Error processing {city}: {e}")
        continue
