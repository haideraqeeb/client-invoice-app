import re

def read_script_file():
    """Read the script.gs file from root directory"""
    try:
        with open('script.gs', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

def update_script_config(script_content, template_file_id, dest_folder_id):
    """Update the CONFIG section in the script with user-provided IDs"""
    if not script_content:
        return None
    
    # Replace TEMPLATE_FILE_ID
    script_content = re.sub(
        r"TEMPLATE_FILE_ID:\s*'[^']*'",
        f"TEMPLATE_FILE_ID: '{template_file_id}'",
        script_content
    )
    
    # Replace DEST_FOLDER_ID
    script_content = re.sub(
        r"DEST_FOLDER_ID:\s*'[^']*'",
        f"DEST_FOLDER_ID: '{dest_folder_id}'",
        script_content
    )
    
    return script_content