#!/usr/bin/env python3
"""
Deep audit of all internal links in .mdx files.
Checks for:
1. Absolute paths starting with /
2. Links with file extensions (.md, .mdx)
3. Links with ./ prefix
4. Cross-module links that might be broken
5. Links to non-existent pages
"""
import os
import re
from pathlib import Path
import json

DOCS_DIR = Path(__file__).parent.resolve()

# Load mint.json to get valid pages
with open(DOCS_DIR / "mint.json", "r") as f:
    mint_config = json.load(f)

# Build set of valid page paths from mint.json
VALID_PAGES = set()
for group in mint_config.get("navigation", []):
    for page in group.get("pages", []):
        VALID_PAGES.add(page)

# All link patterns
LINK_PATTERNS = [
    # Standard markdown links
    re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
]

def get_all_mdx_files():
    """Get all .mdx files in docs directory."""
    return list(DOCS_DIR.rglob("*.mdx"))

def is_internal_link(path):
    """Check if a link is internal (not external URL or image)."""
    if path.startswith(('http://', 'https://', 'mailto:', '#')):
        return False
    if path.startswith('../images/') or path.endswith(('.svg', '.png', '.jpg', '.gif')):
        return False
    return True

def analyze_link(link_path, source_file):
    """Analyze a single link and return issues found."""
    issues = []
    
    # Issue 1: Absolute path starting with /
    if link_path.startswith('/'):
        issues.append(('ABSOLUTE_PATH', f"Link starts with '/': {link_path}"))
    
    # Issue 2: Has file extension
    if link_path.endswith('.md') or link_path.endswith('.mdx'):
        issues.append(('HAS_EXTENSION', f"Link has file extension: {link_path}"))
    
    # Issue 3: Has ./ prefix (sibling links should be bare)
    if link_path.startswith('./'):
        issues.append(('DOT_SLASH', f"Link has './' prefix: {link_path}"))
    
    # Issue 4: Validate target exists
    # Resolve the link path relative to source file
    source_dir = source_file.parent
    if link_path.startswith('/'):
        # Absolute path from docs root
        target = link_path.lstrip('/')
    elif link_path.startswith('../'):
        # Parent directory reference
        target = (source_dir / link_path).resolve().relative_to(DOCS_DIR)
        target = str(target).replace('.mdx', '').replace('.md', '')
    else:
        # Sibling or bare path
        clean_path = link_path.lstrip('./')
        clean_path = clean_path.replace('.mdx', '').replace('.md', '')
        # Get module folder from source file
        rel_source = source_file.relative_to(DOCS_DIR)
        if '/' in str(rel_source):
            module_dir = str(rel_source).split('/')[0]
            target = f"{module_dir}/{clean_path}"
        else:
            target = clean_path
    
    # Check if target is in valid pages
    target_str = str(target).replace('.mdx', '').replace('.md', '')
    if target_str not in VALID_PAGES:
        # Try without leading path components
        base_target = target_str.split('/')[-1] if '/' in target_str else target_str
        possible_matches = [p for p in VALID_PAGES if p.endswith(base_target)]
        if not possible_matches:
            issues.append(('INVALID_TARGET', f"Target not in mint.json: {target_str} (from {link_path})"))
    
    return issues

def fix_link(link_path, source_file):
    """Fix a link and return the corrected version."""
    original = link_path
    
    # Skip external links and images
    if not is_internal_link(link_path):
        return link_path
    
    # Fix 1: Remove ./ prefix
    if link_path.startswith('./'):
        link_path = link_path[2:]
    
    # Fix 2: Remove file extensions
    if link_path.endswith('.md'):
        link_path = link_path[:-3]
    elif link_path.endswith('.mdx'):
        link_path = link_path[:-4]
    
    # Fix 3: Convert absolute paths to relative
    if link_path.startswith('/'):
        # Get source module
        source_rel = source_file.relative_to(DOCS_DIR)
        source_module = str(source_rel).split('/')[0] if '/' in str(source_rel) else None
        
        # Get target module
        target = link_path.lstrip('/')
        target_module = target.split('/')[0] if '/' in target else None
        
        if source_module == target_module:
            # Same module, use bare path
            link_path = target.split('/')[-1] if '/' in target else target
        else:
            # Cross-module, use ../module/page format
            link_path = f"../{target}"
    
    return link_path

def process_file(file_path, fix=True):
    """Process a single file, analyzing and optionally fixing links."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_issues = []
    fixed_content = content
    
    for pattern in LINK_PATTERNS:
        for match in pattern.finditer(content):
            link_text = match.group(1)
            link_path = match.group(2)
            
            if not is_internal_link(link_path):
                continue
            
            issues = analyze_link(link_path, file_path)
            if issues:
                file_issues.extend([(file_path, link_text, link_path, issue) for issue in issues])
            
            if fix:
                fixed_path = fix_link(link_path, file_path)
                if fixed_path != link_path:
                    fixed_content = fixed_content.replace(
                        f'[{link_text}]({link_path})',
                        f'[{link_text}]({fixed_path})'
                    )
    
    if fix and fixed_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        return file_issues, True
    
    return file_issues, False

def main():
    print("=" * 70)
    print("DEEP INTERNAL LINK AUDIT")
    print("=" * 70)
    
    mdx_files = get_all_mdx_files()
    print(f"\nScanning {len(mdx_files)} .mdx files...\n")
    
    all_issues = []
    fixed_files = []
    
    for file_path in sorted(mdx_files):
        issues, was_fixed = process_file(file_path, fix=True)
        all_issues.extend(issues)
        if was_fixed:
            fixed_files.append(file_path)
    
    # Print summary
    print("-" * 70)
    print("ISSUES FOUND AND FIXED:")
    print("-" * 70)
    
    # Group by issue type
    issue_types = {}
    for file_path, link_text, link_path, (issue_type, issue_desc) in all_issues:
        if issue_type not in issue_types:
            issue_types[issue_type] = []
        issue_types[issue_type].append((file_path, link_text, link_path, issue_desc))
    
    for issue_type, issues in issue_types.items():
        print(f"\n{issue_type} ({len(issues)} occurrences):")
        for file_path, link_text, link_path, desc in issues[:5]:  # Show first 5
            rel_path = file_path.relative_to(DOCS_DIR)
            print(f"  [{rel_path}] [{link_text}] -> {link_path}")
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more")
    
    print("\n" + "-" * 70)
    print(f"SUMMARY: Fixed {len(fixed_files)} files with {len(all_issues)} issues")
    print("-" * 70)
    
    if fixed_files:
        print("\nFixed files:")
        for f in fixed_files:
            print(f"  ✓ {f.relative_to(DOCS_DIR)}")

if __name__ == "__main__":
    main()
