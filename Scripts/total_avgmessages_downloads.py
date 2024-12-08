
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
                "includeNSFW": True,
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
total_messages = 0
total_downloads = 0
character_count = 0

# Iterate over cursors from 0 to 10000, increasing by 50
for cursor in range(0, 10001, 50):
    characters = get_character_data(cursor)
    for char in characters:
        total_messages += char['_count']['CharacterMessage']
        total_downloads += char['_count']['CharacterDownload']
        character_count += 1

# Calculate and print the averages, rounded to two decimal places
if character_count > 0:
    avg_messages = round(total_messages / character_count, 2)
    avg_downloads = round(total_downloads / character_count, 2)
    print(f"Total Characters: {character_count}")
    print(f"Average CharacterMessage: {avg_messages}")
    print(f"Average CharacterDownload: {avg_downloads}")
else:
    print("No characters found.")
