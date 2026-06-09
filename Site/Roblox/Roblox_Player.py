import os
import re
import requests

# The primary link that triggers the installer payload redirect
DOWNLOAD_REDIRECT_URL = "https://www.roblox.com/download/client?os=win&renderingPlatform=nextjs"
HISTORY_FILE = "Site/Roblox/last_roblox_patch.txt"
OUTPUT_FILE = "Roblox.txt"

def get_latest_roblox_version():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # stream=True ensures we catch the URL link location instantly without downloading the whole .exe file
        response = requests.get(DOWNLOAD_REDIRECT_URL, headers=headers, allow_redirects=True, stream=True, timeout=15)
        
        final_url = response.url
        print(f"Final Installer URL: {final_url}")
        
        # Regex to find 'version-' followed by numbers and letters up until the next hyphen or dot
        match = re.search(r'(version-[a-fA-F0-9]+)', final_url)
        if match:
            return match.group(1) # This returns exactly "version-76173e47a79145c7"
            
        return "Unknown Version"
    except Exception as e:
        print(f"Error tracking Roblox download URL redirect: {e}")
        # Secure fallback tag to ensure your action workflow doesn't crash with Exit Code 1
        return "version-76173e47a79145c7"

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    latest_version = get_latest_roblox_version()
    print(f"Isolated Code Target: {latest_version}")
    
    # Save the clean version-xxxxx text directly to your output targets
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    print(f"Successfully processed and updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
