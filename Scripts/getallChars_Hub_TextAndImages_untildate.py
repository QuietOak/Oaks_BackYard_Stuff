import os
import requests
import json
import time
from datetime import datetime
import re
import sys

# Configuration
maxpage = 500
newest_characters_url = "https://backyard.ai/api/trpc/hub.character.getNewestCharacters"
character_by_id_url_template = "https://backyard.ai/api/trpc/hub.character.getCharacterById?input=%7B%22json%22%3A%22{}%22%7D"
timeout_duration = 10
max_retries = 3
retry_delay = 5

def sanitize_filename(filename, max_length=50):
    """Sanitize a string to be used as a valid file or folder name."""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'\.+$', '', sanitized)
    return sanitized[:max_length]

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

def save_character_data(cursor, backup_folder, target_date):
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
                    created_at = datetime.strptime(char['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                    if created_at >= target_date:
                        ai_display_name = char['aiDisplayName']
                        sanitized_name = sanitize_filename(ai_display_name)
                        character_id = char['id']
                        character_folder = os.path.join(backup_folder, sanitized_name)
                        os.makedirs(character_folder, exist_ok=True)

                        detailed_data = fetch_character_details(character_id)
                        if detailed_data:
                            json_path = os.path.join(character_folder, f"{sanitized_name}.json")
                            with open(json_path, "w", encoding="utf-8") as file:
                                json.dump(detailed_data, file, indent=4)

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: script.py mm-dd-yyyy")
        sys.exit(1)

    try:
        target_date = datetime.strptime(sys.argv[1], "%m-%d-%Y").date()
    except ValueError:
        print("Invalid date format. Please use mm-dd-yyyy.")
        sys.exit(1)

    current_time = datetime.now().strftime("%Y-%m-%d")
    backup_folder = f"hubbackup_all_{current_time}_{target_date}"
    os.makedirs(backup_folder, exist_ok=True)

    for cursor in range(0, maxpage, 50):
        save_character_data(cursor, backup_folder, target_date)

    print(f"Backup complete. Files saved to folder: {backup_folder}")
