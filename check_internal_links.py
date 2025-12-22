
import os
import re

def check_internal_links():
    mdx_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.mdx'):
                mdx_files.append(os.path.join(root, file))

    broken_internal_links = []
    
    # Pattern to match markdown links [text](path)
    # Exclude external links starting with http or mailto
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    for mdx_path in mdx_files:
        mdx_dir = os.path.dirname(mdx_path)
        with open(mdx_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = link_pattern.findall(content)
        for text, path in matches:
            # Skip external links
            if path.startswith(('http', 'mailto', '#')):
                continue
            
            # Skip images (already checked in previous script)
            if path.endswith(('.svg', '.png', '.jpg', '.jpeg', '.gif')):
                continue

            # Try to resolve path
            # Remove any query params or hashes
            clean_path = path.split('?')[0].split('#')[0]
            
            # If path doesn't have an extension, it might be an MDX file
            if not os.path.splitext(clean_path)[1]:
                # Check for .mdx extension
                prospective_path = os.path.normpath(os.path.join(mdx_dir, clean_path + ".mdx"))
                if os.path.exists(prospective_path):
                    # This is a link missing .mdx
                    broken_internal_links.append({
                        'file': mdx_path,
                        'text': text,
                        'original_path': path,
                        'fixed_path': path + ".mdx",
                        'reason': 'Missing .mdx extension'
                    })
                    continue
                
                # Check for index.mdx if it's a directory
                prospective_index = os.path.normpath(os.path.join(mdx_dir, clean_path, "index.mdx"))
                if os.path.exists(prospective_index):
                    broken_internal_links.append({
                        'file': mdx_path,
                        'text': text,
                        'original_path': path,
                        'fixed_path': path if path.endswith('/') else path + "/",
                        'reason': 'Directory missing trailing slash or pointing to index'
                    })
                    continue
            else:
                # Path has extension, check if it exists
                abs_path = os.path.normpath(os.path.join(mdx_dir, clean_path))
                if not os.path.exists(abs_path):
                    broken_internal_links.append({
                        'file': mdx_path,
                        'text': text,
                        'original_path': path,
                        'reason': 'File does not exist'
                    })

    print(f"Scanned {len(mdx_files)} MDX files.")
    print(f"Found {len(broken_internal_links)} potential internal link issues.")
    
    for issue in broken_internal_links:
        print(f"\nFile: {issue['file']}")
        print(f"  Link: [{issue['text']}]({issue['original_path']})")
        print(f"  Reason: {issue['reason']}")
        if 'fixed_path' in issue:
            print(f"  Suggested Fix: {issue['fixed_path']}")

if __name__ == "__main__":
    check_internal_links()
