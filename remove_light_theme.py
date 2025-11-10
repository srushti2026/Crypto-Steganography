#!/usr/bin/env python3
"""
Remove all light theme classes from PixelVault.tsx
"""

import re

def remove_light_theme_from_pixelvault():
    """Remove all light: classes from PixelVault.tsx"""
    
    file_path = 'frontend/src/pages/PixelVault.tsx'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Original content length:", len(content))
    
    # Remove all light: classes using regex
    # This pattern matches "light:" followed by any valid Tailwind class name
    pattern = r'\s*light:[a-zA-Z0-9\-\/\[\]\.\_\:\%\#]+(?:\s|"|\)|>|$)'
    
    # Count matches before removal
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} light theme classes to remove")
    
    # Remove the matches
    updated_content = re.sub(pattern, '', content)
    
    # Clean up any double spaces that might result
    updated_content = re.sub(r'  +', ' ', updated_content)
    
    print("Updated content length:", len(updated_content))
    print("Difference:", len(content) - len(updated_content), "characters removed")
    
    # Write the updated content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Successfully removed all light theme classes from PixelVault.tsx")

if __name__ == "__main__":
    remove_light_theme_from_pixelvault()