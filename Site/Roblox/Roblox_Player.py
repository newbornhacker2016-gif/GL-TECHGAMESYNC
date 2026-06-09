import os
import re
import requests

DOWNLOAD_REDIRECT_URL = "https://www.roblox.com/download/client?os=win&renderingPlatform=nextjs"
HISTORY_FILE = "Site/Roblox/last_roblox_patch.txt"
OUTPUT_FILE = "Roblox.txt"

def get_latest_roblox_version():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # stream=True checks the destination link instantly without downloading the installer
        response = requests.get(DOWNLOAD_REDIRECT_URL, headers=headers, allow_redirects=True, stream=True, timeout=15)
        final_url = response.url
        print(f"Final Installer URL: {final_url}")
        
        # Pulls 'version-' followed by numbers and letters directly
        match = re.search(r'(version-[a-fA-F0-9]+)', final_url)
        if match:
            return match.group(1)
            
        return "version-76173e47a79145c7"
    except Exception as e:
        print(f"Error tracking redirect: {e}")
        return "version-76173e47a79145c7"

def main():
    # Only try to create folders if a path folder exists
    if os.path.dirname(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.dirname(OUTPUT_FILE):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    latest_version = get_latest_roblox_version()
    print(f"Isolated Code Target: {latest_version}")
    
    # Write files directly
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    print(f"Successfully updated version file!")

if __name__ == "__main__":
    main()
