import os
import requests
import json
import time
from datetime import datetime
import argparse

# Version 5: Adjust output JSON structure and add filtering by author.

# Define how many cards to look back starting from newest, increments of 50.
maxpage = 5000

# Base URLs for the API requests
newest_characters_url = "https://backyard.ai/api/trpc/hub.character.getNewestCharacters"
character_by_id_url_template = "https://backyard.ai/api/trpc/hub.character.getCharacterById?input=%7B%22json%22%3A%22{}%22%7D"

# Timeout and retry configuration
timeout_duration = 10  # seconds to wait before timeout
max_retries = 3  # number of retries before giving up
retry_delay = 5  # seconds to wait between retries

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Backup character data by author.")
parser.add_argument("author_name", type=str, help="The username of the author to filter by.")
args = parser.parse_args()
author_name = args.author_name

# Function to fetch the detailed character data using character ID
def fetch_character_details(character_id):
    url = character_by_id_url_template.format(character_id)
    attempt = 0

    while attempt < max_retries:
        try:
            response = requests.get(url, timeout=timeout_duration)

            if response.status_code == 200:
                original_data = response.json()
                # Reformat to the desired structure
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

# Function to save character data into JSON files
def save_character_data(cursor, backup_folder):
    params = {
        "input": json.dumps({
            "json": {
                "includeNSFW": True,
                "sortBy": {
                    "type": "Newest",
                    "direction": "desc"
                },
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
                    # Check if the character's author matches the provided author name
                    if char['Author']['username'].lower() == author_name.lower():
                        character_id = char['id']
                        ai_display_name = char['aiDisplayName']

                        # Fetch detailed data for the character
                        detailed_data = fetch_character_details(character_id)

                        if detailed_data:
                            # Prepare file name and path
                            file_name = f"{ai_display_name}.json"
                            safe_file_name = "".join(c for c in file_name if c.isalnum() or c in " .-_")
                            file_path = os.path.join(backup_folder, safe_file_name)

                            # Save detailed data to file
                            with open(file_path, "w", encoding="utf-8") as file:
                                json.dump(detailed_data, file, indent=4)

                return  # Exit after successful operation
            else:
                print(f"Failed to retrieve data for cursor {cursor}. Status code: {response.status_code}")
                return
        
        except requests.Timeout:
            attempt += 1
            print(f"Timeout occurred for cursor {cursor}. Retrying {attempt}/{max_retries}...")
            time.sleep(retry_delay)
    
    print(f"Failed to retrieve data after {max_retries} attempts for cursor {cursor}.")

# Create a backup folder with the current date, time, and author name
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_folder = f"hubbackup_{author_name}_{current_time}"
os.makedirs(backup_folder, exist_ok=True)

# Iterate over cursors from 0 to maxpage, increasing by 50
for cursor in range(0, maxpage, 50):
    save_character_data(cursor, backup_folder)

print(f"Backup complete for author '{author_name}'. Files saved to folder: {backup_folder}")
