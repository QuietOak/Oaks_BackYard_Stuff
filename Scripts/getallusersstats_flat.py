import requests
import json
from collections import defaultdict

# Base URL for the API request
url = "https://backyard.ai/api/trpc/hub.character.getNewestCharacters"

# Function to make the API request and extract data for each author
def get_author_stats(cursor):
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
        
        for char in characters:
            author_username = char['Author']['username']
            # Initialize the author's stats if not already in the dictionary
            if author_username not in author_stats:
                author_stats[author_username] = {
                    'Total character count': 0,
                    'Total CharacterDownload': 0,
                    'Total CharacterMessage': 0,
                    'Total Rating': 0.0
                }
            
            # Update stats for the author
            author_stats[author_username]['Total character count'] += 1
            author_stats[author_username]['Total CharacterDownload'] += char['_count']['CharacterDownload']
            author_stats[author_username]['Total CharacterMessage'] += char['_count']['CharacterMessage']
            author_stats[author_username]['Total Rating'] += char.get('rating', 0)
        
    else:
        print(f"Failed to retrieve data for cursor {cursor}. Status code: {response.status_code}")

# Initialize dictionary to store author stats
author_stats = defaultdict(dict)

# Iterate over cursors from 0 to 2000, increasing by 50
for cursor in range(0, 10001, 50):
    get_author_stats(cursor)

# Calculate additional stats and print results for each author
for author, stats in author_stats.items():
    total_characters = stats['Total character count']
    total_downloads = stats['Total CharacterDownload']
    total_messages = stats['Total CharacterMessage']
    total_rating = stats['Total Rating']
    
    # Additional calculations
    messages_per_download = total_messages / total_downloads if total_downloads != 0 else 0
    downloads_per_character = total_downloads / total_characters if total_characters != 0 else 0
    messages_per_character = total_messages / total_characters if total_characters != 0 else 0
    rating_per_character = total_rating / total_characters if total_characters != 0 else 0

    # Print author stats
    print(f"Author: {author}")
    print(f"Total character count: {total_characters}")
    print(f"Total CharacterDownload: {total_downloads}")
    print(f"Total CharacterMessage: {total_messages}")
    print(f"Total Rating: {total_rating}")
    print(f"Messages per Download: {messages_per_download:.2f}")
    print(f"Downloads per Character: {downloads_per_character:.2f}")
    print(f"Messages per Character: {messages_per_character:.2f}")
    print(f"Rating per Character: {rating_per_character:.2f}")
    print("-" * 40)
