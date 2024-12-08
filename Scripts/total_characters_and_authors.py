import time
import requests
import json
from collections import defaultdict

# Base URL for the API request
url = "https://backyard.ai/api/trpc/hub.character.getNewestCharacters"

# Function to make the API request and extract character data with retries
def get_character_data(cursor, retries=3, delay=2):
    attempt = 0
    while attempt < retries:
        try:
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
            response = requests.get(url, params=params, timeout=10)  # Set a timeout for each request
            
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                characters = data['result']['data']['json']['characters']
                return characters
            else:
                print(f"Failed to retrieve data for cursor {cursor}. Status code: {response.status_code}")
                return []

        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            attempt += 1
            print(f"Attempt {attempt} failed for cursor {cursor}. Retrying in {delay} seconds... ({str(e)})")
            time.sleep(delay)
    
    # After retries, give up on this cursor
    print(f"Failed to retrieve data for cursor {cursor} after {retries} retries.")
    return []

# Dictionary to store author character counts
author_character_counts = defaultdict(int)

# Iterate over cursors from 0 to 10000, increasing by 50
for cursor in range(0, 10001, 50):
    characters = get_character_data(cursor)
    if not characters:
        # If no characters are retrieved, log and continue
        continue
    
    for char in characters:
        # Increment the character count for the author
        author_character_counts[char['Author']['username']] += 1

# Calculate the average number of characters per author
total_authors = len(author_character_counts)
total_characters = sum(author_character_counts.values())

if total_authors > 0:
    avg_characters_per_author = round(total_characters / total_authors, 2)
    print(f"Total Authors: {total_authors}")
    print(f"Total Characters: {total_characters}")
    print(f"Average Characters per Author: {avg_characters_per_author}")
else:
    print("No authors found.")
