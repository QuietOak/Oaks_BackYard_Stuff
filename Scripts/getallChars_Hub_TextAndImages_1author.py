import os
import requests
import json
import time
from datetime import datetime
import argparse

# Configuration
maxpage = 10000
newest_characters_url = "https://backyard.ai/api/trpc/hub.character.getNewestCharacters"
character_by_id_url_template = "https://backyard.ai/api/trpc/hub.character.getCharacterById?input=%7B%22json%22%3A%22{}%22%7D"
timeout_duration = 10
max_retries = 3
retry_delay = 5

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Backup character data by author.")
parser.add_argument("author_name", type=str, help="The username of the author to filter by.")
args = parser.parse_args()
author_name = args.author_name

def fetch_character_details(character_id):
    url = character_by_id_url_template.format(character_id)
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(url, timeout=timeout_duration)
            if response.status_code == 200:
                original_data = response.json()
                reformatted_data = {
                    "data": {
                        "json": {
                            "character": original_data['result']['data']['json']
                        }
                    }
                }
                return reformatted_data
            else:
                print(f"Failed to retrieve details for ID {character_id}. Status code: {response.status_code}")
                return None
        except requests.Timeout:
            attempt += 1
            print(f"Timeout occurred for ID {character_id}. Retrying {attempt}/{max_retries}...")
            time.sleep(retry_delay)
    print(f"Failed to retrieve character details after {max_retries} attempts for ID {character_id}.")
    return None

def download_images(images, folder):
    for index, image in enumerate(images, start=1):  # Start numbering images at 1
        image_url = image['imageUrl']
        image_name = f"image{index}.jpg"  # Name images sequentially
        image_path = os.path.join(folder, image_name)
        attempt = 0
        while attempt < max_retries:
            try:
                response = requests.get(image_url, timeout=timeout_duration)
                if response.status_code == 200:
                    with open(image_path, "wb") as img_file:
                        img_file.write(response.content)
                    print(f"Downloaded image: {image_name}")
                    break
                else:
                    print(f"Failed to download image {image_url}. Status code: {response.status_code}")
            except requests.Timeout:
                attempt += 1
                print(f"Timeout for image {image_url}. Retrying {attempt}/{max_retries}...")
                time.sleep(retry_delay)

def save_character_data(cursor, backup_folder):
    params = {
        "input": json.dumps({
            "json": {
                "includeNSFW": True,
                "sortBy": {"type": "Newest", "direction": "desc"},
                "cursor": cursor
            }
        })
    }
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(newest_characters_url, params=params, timeout=timeout_duration)
            if response.status_code == 200:
                data = response.json()
                characters = data['result']['data']['json']['characters']
                for char in characters:
                    if char['Author']['username'].lower() == author_name.lower():
                        ai_display_name = char['aiDisplayName']
                        character_id = char['id']
                        character_folder = os.path.join(backup_folder, ai_display_name)
                        os.makedirs(character_folder, exist_ok=True)

                        detailed_data = fetch_character_details(character_id)
                        if detailed_data:
                            json_path = os.path.join(character_folder, f"{ai_display_name}.json")
                            with open(json_path, "w", encoding="utf-8") as file:
                                json.dump(detailed_data, file, indent=4)

                            # Correctly extract images from the nested structure
                            images = detailed_data['data']['json']['character']['character'].get('Images', [])
                            if images:
                                download_images(images, character_folder)
                return
            else:
                print(f"Failed to retrieve data for cursor {cursor}. Status code: {response.status_code}")
                return
        except requests.Timeout:
            attempt += 1
            print(f"Timeout occurred for cursor {cursor}. Retrying {attempt}/{max_retries}...")
            time.sleep(retry_delay)
    print(f"Failed to retrieve data after {max_retries} attempts for cursor {cursor}.")

# Create a backup folder with the author's name
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_folder = f"hubbackup_{author_name}_{current_time}"
os.makedirs(backup_folder, exist_ok=True)

# Iterate over cursors from 0 to maxpage, increasing by 50
for cursor in range(0, maxpage, 50):
    save_character_data(cursor, backup_folder)

print(f"Backup complete for author '{author_name}'. Files saved to folder: {backup_folder}")
