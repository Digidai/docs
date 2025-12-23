
import os
import re
import json
from pathlib import Path

DOCS_DIR = Path(__file__).parent.resolve()
MINT_JSON_PATH = DOCS_DIR / "mint.json"

def get_all_mdx_files():
    return [str(p.relative_to(DOCS_DIR)) for p in DOCS_DIR.rglob("*.mdx")]

def get_mint_json_files():
    try:
        with open(MINT_JSON_PATH, 'r') as f:
            data = json.load(f)
        
        pages = []
        
        def extract_pages(nav_item):
            if isinstance(nav_item, str):
                pages.append(nav_item if nav_item.endswith('.mdx') else nav_item + '.mdx')
            elif isinstance(nav_item, dict):
                if 'pages' in nav_item:
                    for p in nav_item['pages']:
                        extract_pages(p)
        
        if 'navigation' in data:
            for item in data['navigation']:
                extract_pages(item)
                
        return set(pages)
    except Exception as e:
        print(f"Error reading mint.json: {e}")
        return set()

def check_punctuation(file_path):
    issues = []
    with open(DOCS_DIR / file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Pattern: Chinese character followed by English comma/period, or English comma/period followed by Chinese
    # Note: excluding code blocks would be ideal, but simply checking lines starting with ``` is a rough heuristic
    in_code_block = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            continue
            
        # Check for English comma after Chinese
        if re.search(r'[\u4e00-\u9fa5],[^0-9]', line):
            issues.append(f"Line {i+1}: English comma after Chinese")
            
        # Check for English period after Chinese (excluding file extensions like .md)
        if re.search(r'[\u4e00-\u9fa5]\.(?![a-zA-Z])', line):
             issues.append(f"Line {i+1}: English period after Chinese")
             
    return issues

def main():
    print("="*50)
    print("DEEP QUALITY AUDIT REPORT")
    print("="*50)
    
    all_files = set(get_all_mdx_files())
    # Adjust files to match mint.json format (usually no extension or relative paths)
    # But let's just output the list for now
    
    print("\n[1] Punctuation Check (English punctuation in Chinese text)")
    for file_path in sorted(list(all_files)):
        issues = check_punctuation(file_path)
        if issues:
            print(f"\n📄 {file_path}")
            for issue in issues[:3]: # Limit to 3 per file to avoid spam
                print(f"  - {issue}")
            if len(issues) > 3:
                print(f"  ... and {len(issues)-3} more")

if __name__ == "__main__":
    main()
