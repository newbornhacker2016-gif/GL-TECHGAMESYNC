import os
import re
import requests

# The direct launcher short-link that triggers the redirect download
MAIN_URL = "https://link.bullgamez.com/launcher"
HISTORY_FILE = "Site/SF/BullSF/last_bullsf_patch.txt"
OUTPUT_FILE = "BullSF.txt"

def get_latest_bullsf_version():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # allow_redirects=True allows us to follow the path straight to the final .zip download URL
        # We use requests.head so it reads the URL title instantly without downloading the zip data!
        response = requests.head(MAIN_URL, headers=headers, allow_redirects=True, timeout=15)
        
        # Fallback to a standard get stream if the host blockades HEAD calls
        if response.status_code not in [200, 301, 302]:
            response = requests.get(MAIN_URL, headers=headers, allow_redirects=True, stream=True, timeout=15)
            
        final_url = response.url
        print(f"Final Destination URL: {final_url}")
        
        # Regex search for 'LauncherV' followed by numbers (captures V111 or similar pattern elements)
        match = re.search(r'Launcher(V\d+)', final_url, re.IGNORECASE)
        if match:
            return match.group(1) # This isolates exactly "V111"
            
        # Generic safety fallback regex looking for any lone V+digits variant in the link
        match_fallback = re.search(r'(V\d+)', final_url, re.IGNORECASE)
        if match_fallback:
            return match_fallback.group(1)
            
        return None
    except Exception as e:
        print(f"Error resolving download link redirect: {e}")
        return None

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    latest_version = get_latest_bullsf_version()
    if not latest_version:
        print("Could not parse out a specific version string pattern from the link layout.")
        return

    print(f"Isolated Version Output: {latest_version}")
    
    # Bypassing historical gates to write immediately on your first testing action run
    print(f"Writing clean target launcher value '{latest_version}' to tracking logs...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    with open(HISTORY_FILE, "w") as f:
        f.write(latest_version)
        
    print(f"Successfully configured and outputted data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
