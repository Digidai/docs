
import os
import re

def check_images():
    mdx_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.mdx'):
                mdx_files.append(os.path.join(root, file))

    broken_links = []
    found_images = 0

    for mdx_path in mdx_files:
        with open(mdx_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find markdown images: ![alt](path)
        matches = re.findall(r'!\[.*?\]\((.*?)\)', content)
        
        for img_path in matches:
            if not img_path.endswith('.svg'):
                continue
            
            found_images += 1
            # Normalize path relative to the mdx file
            mdx_dir = os.path.dirname(mdx_path)
            # Remove any query params or hashes
            clean_img_path = img_path.split('?')[0].split('#')[0]
            
            full_img_path = os.path.normpath(os.path.join(mdx_dir, clean_img_path))
            
            if not os.path.exists(full_img_path):
                broken_links.append({
                    'mdx': mdx_path,
                    'ref': img_path,
                    'abs': full_img_path
                })

    print(f"Total MDX files scanned: {len(mdx_files)}")
    print(f"Total SVGs found: {found_images}")
    print(f"Broken links found: {len(broken_links)}")
    
    if broken_links:
        print("\nBroken Links Details:")
        for link in broken_links:
            print(f"- File: {link['mdx']}")
            print(f"  Reference: {link['ref']}")
            print(f"  Expected Path: {link['abs']}")
    else:
        print("\nAll SVG links are valid!")

if __name__ == "__main__":
    check_images()
