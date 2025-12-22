
import os
import re

def fix_internal_links():
    mdx_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.mdx'):
                mdx_files.append(os.path.join(root, file))

    fixed_count = 0
    total_files_fixed = 0
    
    # Pattern to match markdown links [text](path)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    for mdx_path in mdx_files:
        mdx_dir = os.path.dirname(mdx_path)
        with open(mdx_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        def replace_link(match):
            nonlocal fixed_count
            text = match.group(1)
            path = match.group(2)
            
            # Skip external links
            if path.startswith(('http', 'mailto', '#')):
                return match.group(0)
            
            # Skip images
            if path.endswith(('.svg', '.png', '.jpg', '.jpeg', '.gif')):
                return match.group(0)

            # Try to resolve path
            # Remove any query params or hashes
            url_parts = path.split('#')
            clean_path = url_parts[0].split('?')[0]
            anchor = "#" + url_parts[1] if len(url_parts) > 1 else ""
            
            # Improved check for extension: only count it if it's alphanumeric and 2-4 chars
            ext = os.path.splitext(clean_path)[1]
            has_valid_ext = ext.startswith('.') and ext[1:].isalnum() and 2 <= len(ext[1:]) <= 4
            
            if not has_valid_ext:
                # Check for .mdx extension
                prospective_path = os.path.normpath(os.path.join(mdx_dir, clean_path + ".mdx"))
                if os.path.exists(prospective_path):
                    fixed_count += 1
                    return f'[{text}]({clean_path}.mdx{anchor})'
                
                # Check for index.mdx
                prospective_index = os.path.normpath(os.path.join(mdx_dir, clean_path, "index.mdx"))
                if os.path.exists(prospective_index):
                    fixed_count += 1
                    new_path = clean_path if clean_path.endswith('/') else clean_path + "/"
                    if not new_path.endswith('index.mdx'):
                        new_path += "index.mdx"
                    return f'[{text}]({new_path}{anchor})'
            
            return match.group(0)

        new_content = link_pattern.sub(replace_link, content)
        
        if new_content != content:
            with open(mdx_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed links in {mdx_path}")
            total_files_fixed += 1

    print(f"\nTotal links fixed: {fixed_count}")
    print(f"Total files updated: {total_files_fixed}")

if __name__ == "__main__":
    fix_internal_links()
