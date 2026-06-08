import os
import requests
from bs4 import BeautifulSoup

# League of Legends Philippines Patch Notes Feed
MAIN_URL = "https://www.leagueoflegends.com/en-ph/news/tags/patch-notes/"
HISTORY_FILE = "Site/Steam/Dota2/last_lol_patch.txt"
OUTPUT_FILE = "Steam/League Of Legends.txt" # Where it saves the plain text

def get_latest_lol_patch():
    response = requests.get(MAIN_URL)
    if response.status_code != 200:
        print("Failed to access LoL patches page")
        return None, None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Riot wraps links inside an <a> tag. We need to find the one that mentions "Patch" and "Notes"
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        text = link.get_text().strip()
        
        # Check if the text or link contains "patch" and "notes"
        if "patch" in href.lower() and "notes" in href.lower():
            # Convert relative URL to an absolute URL if needed
            if href.startswith("/"):
                href = f"https://www.leagueoflegends.com{href}"
            return href, text
            
    return None, None

def extract_text_from_patch(url):
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to fetch specific LoL patch notes text."
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Strip scripts, navigation, and styles to leave pure raw text
    for element in soup(["script", "style", "nav", "footer"]):
        element.extract()
        
    return soup.get_text(separator="\n", strip=True)

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_url, patch_title = get_latest_lol_patch()
    if not latest_url:
        print("No LoL patch notes URL found.")
        return

    print(f"Found latest live LoL patch: {patch_title} -> {latest_url}")
    
    last_saved_url = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            last_saved_url = f.read().strip()
            
    if latest_url != last_saved_url:
        print("New League patch detected! Extracting text layout...")
        
        with open(HISTORY_FILE, "w") as f:
            f.write(latest_url)
            
        text_output = extract_text_from_patch(latest_url)
        
        # Completely overwrites the old text with the brand new patch text
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(text_output)
            
        print(f"LoL plain text notes saved successfully to {OUTPUT_FILE}")
    else:
        print("No new League of Legends patch detected since yesterday.")

if __name__ == "__main__":
    main()
