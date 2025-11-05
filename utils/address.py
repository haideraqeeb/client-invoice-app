import re

def convert_address_to_three_lines(address):
    """
    Convert single line address to exactly 3 lines.
    Handles all edge cases and ensures exactly 3 lines output.
    """
    if not address or address.strip() == '':
        return '<br><br>'
    
    address = address.strip()
    
    # Remove any existing line breaks or HTML tags
    address = address.replace('\n', ' ').replace('\r', ' ')
    address = address.replace('<br>', ' ').replace('<BR>', ' ')
    
    # Normalize spaces
    address = re.sub(r'\s+', ' ', address).strip()
    
    # Split by common delimiters: comma, semicolon, pipe
    parts = re.split(r'[,;|]', address)
    parts = [p.strip() for p in parts if p.strip()]
    
    if len(parts) == 0:
        return '<br><br>'
    
    # If only 1 part, try to split by long spaces or dashes
    if len(parts) == 1:
        # Try splitting by multiple spaces (2 or more)
        parts = re.split(r'\s{2,}', parts[0])
        parts = [p.strip() for p in parts if p.strip()]
    
    # If still only 1 part, split by reasonable word count
    if len(parts) == 1:
        words = parts[0].split()
        if len(words) <= 3:
            # Very short address, put on line 1
            return parts[0] + '<br><br>'
        elif len(words) <= 6:
            # Split into 2 parts
            mid = len(words) // 2
            parts = [' '.join(words[:mid]), ' '.join(words[mid:])]
        else:
            # Split into 3 parts
            third = len(words) // 3
            parts = [
                ' '.join(words[:third]),
                ' '.join(words[third:2*third]),
                ' '.join(words[2*third:])
            ]
    
    # Now distribute parts into exactly 3 lines
    if len(parts) == 1:
        return parts[0] + '<br><br>'
    elif len(parts) == 2:
        return parts[0] + '<br>' + parts[1] + '<br>'
    elif len(parts) == 3:
        return '<br>'.join(parts)
    else:
        # More than 3 parts: distribute evenly
        parts_per_line = len(parts) / 3.0
        
        lines = []
        current_line_parts = []
        target_parts = parts_per_line
        
        for i, part in enumerate(parts):
            current_line_parts.append(part)
            
            # Check if we should move to next line
            if len(lines) < 2 and len(current_line_parts) >= target_parts:
                lines.append(', '.join(current_line_parts))
                current_line_parts = []
                target_parts = (len(parts) - sum(len(l.split(', ')) for l in lines)) / (3 - len(lines))
        
        # Add remaining parts to last line
        if current_line_parts:
            lines.append(', '.join(current_line_parts))
        
        # Ensure exactly 3 lines
        while len(lines) < 3:
            lines.append('')
        
        return '<br>'.join(lines[:3])