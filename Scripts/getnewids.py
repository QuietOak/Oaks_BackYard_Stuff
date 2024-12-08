import requests
import json

#example request for ref
#https://backyard.ai/api/trpc/hub.character.getNewestCharacters?input=%7B%22json%22%3A%7B%22includeNSFW%22%3Atrue%2C%22sortBy%22%3A%7B%22type%22%3A%22Newest%22%2C%22direction%22%3A%22desc%22%7D%2C%22cursor%22%3A50%7D%7D

# Base URL for the API request
url = "https://backyard.ai/api/trpc/hub.character.getNewestCharacters"

# Function to make the API request and extract character IDs
def get_character_ids(cursor):
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
        return [char['id'] for char in characters]
    else:
        print(f"Failed to retrieve data for cursor {cursor}. Status code: {response.status_code}")
        return []

# Initialize list to store all character IDs
all_character_ids = []

# Iterate over cursors from 0 to 2000, increasing by 50
for cursor in range(0, 10001, 50):
    character_ids = get_character_ids(cursor)
    all_character_ids.extend(character_ids)

# Print all character IDs
print(f"Total character IDs collected: {len(all_character_ids)}")
##print(all_character_ids)
