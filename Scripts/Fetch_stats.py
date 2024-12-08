import requests
import json
from datetime import datetime
import argparse
import time

# Argument parser to get the username from command line
parser = argparse.ArgumentParser()
parser.add_argument("username")
args = parser.parse_args()

# Capture the current time
current_time = datetime.now()

# Timeout and retry configuration
timeout_duration = 10  # seconds to wait before timeout
max_retries = 3  # number of retries before giving up
retry_delay = 5  # seconds to wait between retries

# Initialize total sums
total_entries = 0
total_counts = {key: 0 for key in ["_count.CharacterDownload", "_count.CharacterMessage", "rating"]}
invalid_characters = []  # List to track characters with invalid data

# Function to validate the fetched data
def is_valid_character_data(character):
    # Check if required keys are non-zero
    keys_to_check = ["_count.CharacterDownload", "_count.CharacterMessage", "rating"]
    
    for key in keys_to_check:
        value = character
        nested_keys = key.split(".")
        for nested_key in nested_keys:
            value = value.get(nested_key, {})
        if value == 0:
            return False
    return True

# Function to fetch data with validation, API timeout handling, and retry mechanism
def fetch_data(username, cursor_value):
    # Define the URL parameters
    url_params = {
        "json": {
            "username": username,
            "includeNSFW": True,
            "sortBy": {"type": "Trending", "direction": "desc"},
            "cursor": cursor_value
        }
    }

    # Format the URL
    url = "https://backyard.ai/api/trpc/hub.user.getUserByUsername?input=" + json.dumps(url_params)

    attempt = 0
    while attempt < max_retries:
        try:
            # Send a GET request to the URL with timeout
            response = requests.get(url, timeout=timeout_duration)

            # Check if the request was successful
            if response.status_code == 200:
                try:
                    # Load JSON data
                    json_data = response.json()

                    # Extract necessary information
                    characters = json_data["result"]["data"]["json"]["user"]["Characters"]

                    # Initialize sums for the current request
                    sums = {key: 0 for key in ["_count.CharacterDownload", "_count.CharacterMessage", "rating"]}

                    # Count number of entries
                    num_entries = 0

                    # Sum up values, only if the data is valid
                    for character in characters:
                        if is_valid_character_data(character):
                            num_entries += 1
                            for key in sums:
                                value = character
                                nested_keys = key.split(".")
                                for nested_key in nested_keys:
                                    value = value.get(nested_key, {})
                                sums[key] += value
                        else:
                            print(f"Invalid data found for character ID {character['id']}. Logging for retry...")
                            invalid_characters.append(character["id"])

                    return num_entries, sums

                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Error parsing or validating data: {e}")
                    attempt += 1
                    time.sleep(retry_delay)
            else:
                print(f"Failed to retrieve data for cursor {cursor_value}. Status code:", response.status_code)
                attempt += 1
                time.sleep(retry_delay)

        except requests.Timeout:
            attempt += 1
            print(f"Timeout occurred for cursor {cursor_value}. Retrying {attempt}/{max_retries}...")
            time.sleep(retry_delay)

    print(f"Failed to retrieve valid data after {max_retries} attempts for cursor {cursor_value}.")
    return 0, {}

# Retry fetching individual characters with invalid data
def retry_invalid_characters():
    global invalid_characters
    print("Retrying invalid characters...")

    for character_id in invalid_characters:
        url = f"https://backyard.ai/api/trpc/hub.character.getCharacterById?input={character_id}"
        
        attempt = 0
        while attempt < max_retries:
            try:
                response = requests.get(url, timeout=timeout_duration)
                
                if response.status_code == 200:
                    character = response.json()["result"]["data"]["json"]["character"]

                    if is_valid_character_data(character):
                        print(f"Successfully retrieved valid data for character ID {character_id}")
                        for key in total_counts:
                            value = character
                            nested_keys = key.split(".")
                            for nested_key in nested_keys:
                                value = value.get(nested_key, {})
                            total_counts[key] += value
                    else:
                        print(f"Data for character ID {character_id} is still invalid.")
                    break
                else:
                    print(f"Failed to retrieve data for character ID {character_id}. Status code:", response.status_code)
                    attempt += 1
                    time.sleep(retry_delay)

            except requests.Timeout:
                attempt += 1
                print(f"Timeout occurred for character ID {character_id}. Retrying {attempt}/{max_retries}...")
                time.sleep(retry_delay)

# Call fetch_data function for each cursor value and accumulate the sums
for cursor_value in [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]:
    current_num_entries, current_sums = fetch_data(args.username, cursor_value)
    total_entries += current_num_entries
    for key in total_counts:
        total_counts[key] += current_sums[key]

# Retry any invalid characters found during the process
retry_invalid_characters()

# Print totals
formatted_time = current_time.strftime("%I:%M %p %m/%d/%Y")
print("User:", args.username)
print("Current Time:", formatted_time)
print("Total Characters found:", total_entries)
print("Total counts:")
for key, value in total_counts.items():
    print(f"{key}: {value}")

# Calculate and print ratios
if total_entries > 0:
    message_download_ratio = total_counts["_count.CharacterMessage"] / total_counts["_count.CharacterDownload"]
    print(f"Message/Download Ratio: {message_download_ratio:.2f}")
    for key, value in total_counts.items():
        if key != "_count.CharacterMessage" and key != "_count.CharacterDownload":
            print(f"{key} per Character: {value / total_entries:.2f}")

# Calculate and print per character metrics
if total_entries > 0:
    message_per_character = total_counts["_count.CharacterMessage"] / total_entries
    download_per_character = total_counts["_count.CharacterDownload"] / total_entries
    print(f"Message per Character: {message_per_character:.2f}")
    print(f"Download per Character: {download_per_character:.2f}")
