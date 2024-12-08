import requests
import json
import argparse
from collections import defaultdict

# Base URL for the API request
url = "https://backyard.ai/api/trpc/hub.character.getNewestCharacters"

# Function to make the API request and extract data for each author
def get_author_stats(cursor, filter_tag):
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
            # Check if the character has the specified tag
            tags = [tag['name'] for tag in char['Tags']]
            if filter_tag in tags:
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
                
                # Update overall stats
                overall_stats['Total character count'] += 1
                overall_stats['Total CharacterDownload'] += char['_count']['CharacterDownload']
                overall_stats['Total CharacterMessage'] += char['_count']['CharacterMessage']
                overall_stats['Total Rating'] += char.get('rating', 0)
        
    else:
        print(f"Failed to retrieve data for cursor {cursor}. Status code: {response.status_code}")

# Function to print the stats for each author
def print_author_stats():
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

# Function to print the overall stats
def print_overall_stats():
    total_characters = overall_stats['Total character count']
    total_downloads = overall_stats['Total CharacterDownload']
    total_messages = overall_stats['Total CharacterMessage']
    total_rating = overall_stats['Total Rating']

    # Additional calculations
    messages_per_download = total_messages / total_downloads if total_downloads != 0 else 0
    downloads_per_character = total_downloads / total_characters if total_characters != 0 else 0
    messages_per_character = total_messages / total_characters if total_characters != 0 else 0
    rating_per_character = total_rating / total_characters if total_characters != 0 else 0

    # Print overall stats
    print("Overall Stats:")
    print(f"Total character count: {total_characters}")
    print(f"Total CharacterDownload: {total_downloads}")
    print(f"Total CharacterMessage: {total_messages}")
    print(f"Total Rating: {total_rating}")
    print(f"Messages per Download: {messages_per_download:.2f}")
    print(f"Downloads per Character: {downloads_per_character:.2f}")
    print(f"Messages per Character: {messages_per_character:.2f}")
    print(f"Rating per Character: {rating_per_character:.2f}")
    print("=" * 40)

# Main execution
if __name__ == "__main__":
    # Parse the command line argument for the tag filter
    parser = argparse.ArgumentParser(description="Filter characters by tag and display stats.")
    parser.add_argument("tag", type=str, help="Tag to filter characters by")
    args = parser.parse_args()
    filter_tag = args.tag

    # Initialize dictionary to store author stats
    author_stats = defaultdict(dict)

    # Initialize dictionary to store overall stats
    overall_stats = {
        'Total character count': 0,
        'Total CharacterDownload': 0,
        'Total CharacterMessage': 0,
        'Total Rating': 0.0
    }

    # Iterate over cursors from 0 to 10000, increasing by 50
    for cursor in range(0, 10001, 50):
        get_author_stats(cursor, filter_tag)

    # Print author stats and overall stats
    print_author_stats()
    print_overall_stats()
