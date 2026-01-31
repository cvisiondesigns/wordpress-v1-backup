import os
import re

ROOT_DIR = '/Users/CLMB/Documents/GitHub/wordpress-v1-backup'
DIR_MAP = {}
MANUAL_MAP = {
    'package': 'package-design'
}

def build_dir_map():
    print("Building directory map...")
    for root, dirs, files in os.walk(ROOT_DIR):
        for d in dirs:
            if d not in DIR_MAP:
                DIR_MAP[d] = os.path.join(root, d)
    print(f"Mapped {len(DIR_MAP)} directories.")

def fix_path(current_file_path, link_path):
    """
    Converts an absolute link (starting with /) to a relative path
    based on the current file's location.
    
    Args:
        current_file_path: Absolute path to the HTML file being processed.
        link_path: The link found in the file (e.g., "/cwp/style.css").
        
    Returns:
        The relative path (e.g., "../cwp/style.css").
    """
    if not link_path.startswith('/'):
        return link_path
    
    # Handle protocol relative URLs or ignore specific cases if needed
    if link_path.startswith('//'):
        return link_path

    # Construct the full path to the target
    # Remove the leading slash from link_path to join correctly
    target_abs_path = os.path.join(ROOT_DIR, link_path.lstrip('/'))
    
    # Handle directory links - try to find index.html if it's a folder
    if link_path.endswith('/'):
         if os.path.exists(os.path.join(target_abs_path, 'index.html')):
             target_abs_path = os.path.join(target_abs_path, 'index.html')
    # Special case for root "/"
    elif link_path == "/":
         target_abs_path = os.path.join(ROOT_DIR, 'index.html')

    # Check if target exists, if not, try to find it via map
    # This part handles "absolute" paths that are wrong
    if not os.path.exists(target_abs_path):
        # Extract the last directory name
        # e.g. /cwp/web-design/ -> web-design
        parts = link_path.strip('/').split('/')
        if parts:
            candidate = parts[-1]
            if candidate in MANUAL_MAP:
                 candidate = MANUAL_MAP[candidate]
            
            if candidate in DIR_MAP:
                 # Found it elsewhere!
                 new_target = DIR_MAP[candidate]
                 # specific check: if original link ended in /, look for index.html
                 if os.path.exists(os.path.join(new_target, 'index.html')):
                     target_abs_path = os.path.join(new_target, 'index.html')
                 else:
                     target_abs_path = new_target

    # Calculate relative path
    current_dir = os.path.dirname(current_file_path)
    rel_path = os.path.relpath(target_abs_path, current_dir)
    
    return rel_path

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Regex patterns
    # 1. src="..."
    # 2. href="..."
    # 3. url(...) for CSS inside HTML
    
    def replace_match(match):
        attr = match.group(1) # src= or href= or url(
        quote = match.group(2) # " or ' or empty for url()
        link = match.group(3)
        
        # Don't touch relative paths, anchors, or external links
        # But checking if they are potentially broken relative links that need fixing
        
        # strip query params for existence check
        clean_link = link.split('?')[0].split('#')[0]
        
        # If it's already absolute (starts with /), let the existing logic handle it (which we improved to strip cwp)
        # But if it's relative (e.g. ../cwp/about/), we need to catch it here.
        if not link.startswith('/') and not link.startswith('http') and not link.startswith('#') and not link.startswith('mailto:'):
             current_dir = os.path.dirname(file_path)
             abs_from_current = os.path.normpath(os.path.join(current_dir, clean_link))
             
             # Logic for EXISTING relative paths
             if os.path.exists(abs_from_current):
                 # If it points to a directory, we generally want index.html for local browsing
                 if os.path.isdir(abs_from_current):
                     if os.path.exists(os.path.join(abs_from_current, 'index.html')):
                         target = os.path.join(abs_from_current, 'index.html')
                         rel_path = os.path.relpath(target, current_dir)
                         return f'{attr}{quote}{rel_path}{quote}'
             
             # Logic for BROKEN relative paths (stripping /cwp/ or mapping)
             else:
                  # Try stripping /cwp/ from the absolute path if it exists
                  # We iterate to find 'cwp' path segment and remove it
                  # Simple string replace for now as specific to this project
                  target = None
                  
                  if '/cwp/' in abs_from_current:
                       # Only strip if NOT followed by wp-content/wp-includes
                       if not ('/cwp/wp-content' in abs_from_current or '/cwp/wp-includes' in abs_from_current):
                           abs_no_cwp = abs_from_current.replace('/cwp/', '/')
                           
                           # Check if THIS exists
                           if os.path.exists(abs_no_cwp):
                                if os.path.isdir(abs_no_cwp):
                                    if os.path.exists(os.path.join(abs_no_cwp, 'index.html')):
                                         target = os.path.join(abs_no_cwp, 'index.html')
                                    else:
                                         target = abs_no_cwp
                                else:
                                    target = abs_no_cwp
                  
                  # Try looking up the directory name in DIR_MAP if stripped path failed
                  if not target:
                       parts = clean_link.strip('/').split('/')
                       if parts:
                            candidate = parts[-1]
                            # Check Manual Map
                            if candidate in MANUAL_MAP:
                                candidate = MANUAL_MAP[candidate]
                                
                            if candidate in DIR_MAP:
                                target = DIR_MAP[candidate]
                                if os.path.isdir(target) and os.path.exists(os.path.join(target, 'index.html')):
                                     target = os.path.join(target, 'index.html')
                  
                  if target:
                       # Found the correct target!
                       # Calculate new relative path
                       rel_path = os.path.relpath(target, current_dir)
                       return f'{attr}{quote}{rel_path}{quote}'

             if not link.startswith('/'):
                 return match.group(0)
        
        # New Logic: Strip /cwp/ prefix if it's NOT a resource file
        # Resources are in wp-content or wp-includes
        # We need to act on the POTENTIALLY modified link (which might now start with /)
        
        temp_link = link
        if temp_link.startswith('/cwp/'):
             if not (temp_link.startswith('/cwp/wp-content') or temp_link.startswith('/cwp/wp-includes')):
                  temp_link = temp_link.replace('/cwp/', '/', 1)
        
        new_link = fix_path(file_path, temp_link)
        
        # Reconstruct the string
        if attr.strip().startswith('url'):
             return f'{attr}{quote}{new_link}{quote}'
        return f'{attr}{quote}{new_link}{quote}'

    # Pattern for src/href: (src=|href=)(['"])(.*?)(['"])
    # Extended to include data-src, poster, etc.
    pattern_html = re.compile(r'(src=|href=|data-src=|poster=)(["\'])([^"\']*?)(\2)', re.IGNORECASE)
    content = pattern_html.sub(replace_match, content)

    # Pattern for srcset/data-srcset: These contain comma-separated URLs with space-separated descriptors
    pattern_srcset = re.compile(r'(srcset=|data-srcset=)(["\'])([^"\']*?)(\2)', re.IGNORECASE)
    
    def replace_srcset_match(match):
        attr = match.group(1)
        quote = match.group(2)
        val = match.group(3)
        
        # Split by comma
        parts = val.split(',')
        new_parts = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Split by space to separate URL and descriptor
            subparts = part.split()
            if not subparts:
                continue
                
            url = subparts[0]
            descriptor = " ".join(subparts[1:]) if len(subparts) > 1 else ""
            
            # Reuse similar logic
            temp_link = url
            
            if url.startswith('/'):
                 # Check existing path
                 check_path = os.path.join(ROOT_DIR, url.lstrip('/'))
                 if not os.path.exists(check_path):
                      # Try stripping /cwp/
                      if '/cwp/' in url:
                          test_url = url.replace('/cwp/', '/')
                          test_path = os.path.join(ROOT_DIR, test_url.lstrip('/'))
                          if os.path.exists(test_path):
                               temp_link = test_url
                 
                 # Convert to relative
                 new_url = fix_path(file_path, temp_link)
                 
                 if descriptor:
                     new_parts.append(f"{new_url} {descriptor}")
                 else:
                     new_parts.append(new_url)
            else:
                 new_parts.append(part)
                 
        new_val = ", ".join(new_parts)
        return f'{attr}{quote}{new_val}{quote}'

    content = pattern_srcset.sub(replace_srcset_match, content)

    # Pattern for CSS url(): url(['"]? ... ['"]?)
    # Group 1: url(
    # Group 2: Quote (optional)
    # Group 3: Content
    # Group 4: Quote (optional match group 2)
    pattern_css = re.compile(r'(url\()(["\']?)([^"\')]*?)(["\']?\))', re.IGNORECASE)
    
    def replace_css_match(match):
        start = match.group(1)
        quote = match.group(2)
        link = match.group(3)
        end = match.group(4)
        
        # Reuse same logic? Somewhat risky to recurse replace_match, duplicate logic for now or simple call
        # CSS usually simple URLs
        # Let's simplify and just call fix_path if absolute
        
        if link.startswith('/'):
             temp_link = link
             if temp_link.startswith('/cwp/'):
                 if not (temp_link.startswith('/cwp/wp-content') or temp_link.startswith('/cwp/wp-includes')):
                      temp_link = temp_link.replace('/cwp/', '/', 1)
             new_link = fix_path(file_path, temp_link)
             return f'{start}{quote}{new_link}{end}'
        
        return match.group(0)

    content = pattern_css.sub(replace_css_match, content)

    # Pattern for JSON encoded paths (e.g. \/cwp\/...)
    # We look for \/ followed by path components
    pattern_json = re.compile(r'(\\\/)(cwp|wp-content|wp-includes)(.*?)((?=\\\/)|(?="))', re.IGNORECASE)
    
    def replace_json_match(match):
        prefix = match.group(1) # \/
        folder = match.group(2) # cwp, etc
        rest = match.group(3)
        
        # Calculate relative path but for JSON (replace / with \/)
        # We temporarily create a fake absolute path to calculate relative
        fake_abs = f'/{folder}{rest}'
        fixed_rel = fix_path(file_path, fake_abs)
        
        # Convert back to JSON escaped format
        # fixed_rel will be like ../cwp/...
        # JSON needs ..\/cwp\/...
        json_ready = fixed_rel.replace('/', r'\/')
        return json_ready

    content = pattern_json.sub(replace_json_match, content)

    if content != original_content:
        print(f"Fixed: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    build_dir_map()
    print(f"Scanning directory: {ROOT_DIR}")
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.html') or file.endswith('.htm'):
                process_file(file_path)
                count += 1
    print(f"Processed {count} HTML files.")

if __name__ == '__main__':
    main()
