#!/usr/bin/env python3
"""
Scans all .mdx files for internal links and fixes them to use the correct format.
Removes './' prefix and any file extensions from internal markdown links.
"""
import os
import re
from pathlib import Path

DOCS_DIR = "/Users/dai/Documents/CursorProjects/docs"

# Regex to find markdown links: [text](path)
# Captures: full match, link text, path
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\((\./[^)]+|\.\.\/[^)]+)\)')

def fix_link(match, file_path):
    """Fix a single link match."""
    full_match = match.group(0)
    link_text = match.group(1)
    path = match.group(2)
    
    # Skip image links
    if path.startswith('../images/') or path.startswith('./images/'):
        return full_match
    
    original_path = path
    
    # Remove ./ prefix for sibling links
    if path.startswith('./'):
        path = path[2:]
    
    # Remove file extensions (.md, .mdx)
    if path.endswith('.md'):
        path = path[:-3]
    elif path.endswith('.mdx'):
        path = path[:-4]
    
    if original_path != path:
        return f'[{link_text}]({path})'
    return full_match

def process_file(file_path):
    """Process a single file, fixing links."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find and fix all links
    content = LINK_PATTERN.sub(lambda m: fix_link(m, file_path), content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    mdx_files = list(Path(DOCS_DIR).rglob('*.mdx'))
    
    fixed_files = []
    for file_path in mdx_files:
        if process_file(str(file_path)):
            fixed_files.append(str(file_path))
    
    print(f"Scanned {len(mdx_files)} .mdx files.")
    print(f"Fixed {len(fixed_files)} files:")
    for f in fixed_files:
        print(f"  - {f.replace(DOCS_DIR, '')}")

if __name__ == "__main__":
    main()
