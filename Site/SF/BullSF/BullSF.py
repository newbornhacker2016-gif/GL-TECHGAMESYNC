import os
import re
import requests

MAIN_URL = "https://link.bullgamez.com/launcher"
HISTORY_FILE = "Site/SF/BullSF/last_bullsf_patch.txt"
OUTPUT_FILE = "BullSF.txt"

def get_latest_bullsf_version():
    try:
        # Create a real browser header identity session to bypass bot firewalls
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        })
        
        # stream=True loads only the link text destination without downloading the actual large zip file package
        response = session.get(MAIN_URL, allow_redirects=True, stream=True, timeout=15)
        
        final_url = response.url
        print(f"Final Redirection Link: {final_url}")
        
        # Match 'LauncherV' followed by numbers (e.g., LauncherV111 -> V111)
        match = re.search(r'Launcher(V\d+)', final_url, re.IGNORECASE)
        if match:
            return match.group(1).upper() # Ensures standard formatting like V111
            
        # Fallback to search for any V + digits sequence in the path string
        match_fallback = re.search(r'(V\d+)', final_url, re.IGNORECASE)
        if match_fallback:
            return match_fallback.group(1).upper()
            
        return "Unknown Version"
    except Exception as e:
        print(f"Connection/Redirection Error: {e}")
        return None

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    latest_version = get_latest_bullsf_version()
    if not latest_version:
        print("Could not isolate a valid download URL path destination.")
        return

    print(f"Parsed Target Match: {latest_version}")
    print(f"Writing clean target code '{latest_version}' to tracking files...")
    
    # Clean overwrite format output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    with open(HISTORY_FILE, "w") as f:
        f.write(latest_version)
        
    print(f"Successfully processed and updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
