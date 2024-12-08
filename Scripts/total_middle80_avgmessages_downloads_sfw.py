
import requests
import json

# Base URL for the API request
url = "https://backyard.ai/api/trpc/hub.character.getNewestCharacters"

# Function to make the API request and extract character data
def get_character_data(cursor):
    # Prepare the query parameters
    params = {
        "input": json.dumps({
            "json": {
                "includeNSFW": False,
                "sortBy": {
                    "type": "Newest",
                    "direction": "desc"
                },
                "cursor": cursor
            }
        })
    }
    
    # Make the GET request
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        characters = data['result']['data']['json']['characters']
        return characters
    else:
        print(f"Failed to retrieve data for cursor {cursor}. Status code: {response.status_code}")
        return []

# Initialize lists to store all CharacterMessage and CharacterDownload counts
message_counts = []
download_counts = []
character_count = 0

# Iterate over cursors from 0 to 10000, increasing by 50
for cursor in range(0, 3001, 50):
    characters = get_character_data(cursor)
    for char in characters:
        message_counts.append(char['_count']['CharacterMessage'])
        download_counts.append(char['_count']['CharacterDownload'])
        character_count += 1

# Function to filter out top and bottom 10% of data
def remove_top_and_bottom_10_percent(data):
    data_sorted = sorted(data)
    ten_percent = int(len(data_sorted) * 0.1)
    # Keep only the middle 80% of the data
    filtered_data = data_sorted[ten_percent:-ten_percent]
    return filtered_data

# Remove top and bottom 10% from message_counts and download_counts
filtered_message_counts = remove_top_and_bottom_10_percent(message_counts)
filtered_download_counts = remove_top_and_bottom_10_percent(download_counts)

# Calculate and print the averages, rounded to two decimal places
if len(filtered_message_counts) > 0 and len(filtered_download_counts) > 0:
    avg_messages = round(sum(filtered_message_counts) / len(filtered_message_counts), 2)
    avg_downloads = round(sum(filtered_download_counts) / len(filtered_download_counts), 2)
    print(f"Total Characters: {character_count}")
    middle_count = len(filtered_message_counts)
    print(f"Middle80 Characters: {middle_count}")
    print(f"Average CharacterMessage (filtered): {avg_messages}")
    print(f"Average CharacterDownload (filtered): {avg_downloads}")
else:
    print("No characters found or insufficient data.")
