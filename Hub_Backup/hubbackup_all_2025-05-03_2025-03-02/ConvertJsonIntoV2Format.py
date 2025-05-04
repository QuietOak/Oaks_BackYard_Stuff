import json
import os

def convert_to_v2(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    char_data = data['data']['json']['character']['character']
    char_name = char_data['aiName']
    
    lorebook_items = char_data.get('Lorebook', {}).get('LorebookItems', [])
    
    # Build Lorebook entries
    lorebook_entries = []
    for idx, item in enumerate(lorebook_items, start=1):
        lorebook_entries.append({
            "id": idx,
            "keys": [item['key']],
            "secondary_keys": [],
            "comment": item['key'],
            "content": item['value'],
            "constant": False,
            "selective": False,
            "insertion_order": 50,
            "enabled": True,
            "position": "before_char",
            "case_sensitive": False,
            "name": "",
            "priority": 10,
            "extensions": {}
        })

    # Replace character's name dynamically
    def replace_char_name(text):
        return text.replace("User", "{{user}}").replace(char_name, "{{char}}")

    # Build the V2 format
    v2_data = {
        "data": {
            "name": char_name,
            "description": replace_char_name(char_data['aiPersona']),
            "personality": "",
            "scenario": replace_char_name(char_data['scenario']),
            "first_mes": char_data['firstMessage'],
            "mes_example": replace_char_name(char_data['customDialogue']).replace("#", ""),
            "system_prompt": replace_char_name(char_data['basePrompt']),
            "creator_notes": f"Original character by {char_data['Author']['username']}\nhttps://backyard.ai/hub/character/{char_data['id']}",
            "alternate_greetings": [],
            "character_book": {
                "name": None,
                "description": None,
                "scan_depth": 50,
                "token_budget": 500,
                "recursive_scanning": False,
                "entries": lorebook_entries,
                "extensions": {}
            } if lorebook_items else None,
            "tags": [tag['name'] for tag in char_data['Tags']],
            "creator": char_data['Author']['username'],
            "character_version": "",
        },
        "spec": "chara_card_v2",
        "spec_version": "2.0"
    }

    # Write the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(v2_data, f, ensure_ascii=False, indent=4)

def process_files_in_directory(root_dir="."):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json") and not file.startswith("V2Import_"):
                input_path = os.path.join(root, file)
                output_path = os.path.join(root, f"V2Import_{file}")
                print(f"Processing {input_path} -> {output_path}")
                try:
                    convert_to_v2(input_path, output_path)
                    print(f"Successfully converted {file} to V2 format.")
                except Exception as e:
                    print(f"Failed to convert {file}: {e}")

if __name__ == "__main__":
    process_files_in_directory()
