#!/usr/bin/env python3
"""
Converts all internal sibling links in .mdx files to absolute paths.
Changes: [Title](page-name) -> [Title](/module-XX/page-name)
"""
import os
import re
from pathlib import Path

DOCS_DIR = Path("/Users/dai/Documents/CursorProjects/docs")

# Pattern to find markdown links with bare page names (no / or .. prefix)
# Matches: [text](page-name) but NOT [text](../path) or [text](/path) or [text](http...)
SIBLING_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([a-z0-9][a-z0-9\-\.]+)\)')

def get_module_from_file(file_path):
    """Extract module directory from file path."""
    rel_path = file_path.relative_to(DOCS_DIR)
    parts = str(rel_path).split('/')
    if len(parts) > 1:
        return parts[0]  # e.g., 'module-05', 'appendix'
    return None

def fix_sibling_link(match, module):
    """Convert sibling link to absolute path."""
    link_text = match.group(1)
    page_name = match.group(2)
    
    # Skip if it looks like an image or external
    if page_name.endswith(('.svg', '.png', '.jpg', '.gif', '.webp')):
        return match.group(0)
    
    # Convert to absolute path
    if module:
        return f'[{link_text}](/{module}/{page_name})'
    return match.group(0)

def process_file(file_path):
    """Process a single file, fixing sibling links."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    module = get_module_from_file(file_path)
    
    if module:
        content = SIBLING_LINK_PATTERN.sub(
            lambda m: fix_sibling_link(m, module), 
            content
        )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("=" * 70)
    print("CONVERTING SIBLING LINKS TO ABSOLUTE PATHS")
    print("=" * 70)
    
    mdx_files = list(DOCS_DIR.rglob("*.mdx"))
    print(f"\nScanning {len(mdx_files)} .mdx files...\n")
    
    fixed_files = []
    for file_path in sorted(mdx_files):
        if process_file(file_path):
            fixed_files.append(file_path)
            print(f"  ✓ {file_path.relative_to(DOCS_DIR)}")
    
    print("\n" + "-" * 70)
    print(f"SUMMARY: Fixed {len(fixed_files)} files")
    print("-" * 70)

if __name__ == "__main__":
    main()
