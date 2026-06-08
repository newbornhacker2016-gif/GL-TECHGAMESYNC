import os
import requests
from bs4 import BeautifulSoup

# Riot Games official API endpoint for the PH News patch-notes tag
API_URL = "https://www.leagueoflegends.com/page-data/en-ph/news/tags/patch-notes/page-data.json"

HISTORY_FILE = "Site/Riot/last_lol_patch.txt"
OUTPUT_FILE = "LeagueOfLegend.txt"

def get_latest_lol_patch():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code != 200:
            print(f"API Error: Status {response.status_code}")
            return None, None
            
        data = response.json()
        # Navigate through Riot's JSON tree structure to find the news feed articles
        articles = data.get("result", {}).get("pageContext", {}).get("data", {}).get("allContentstackArticles", {}).get("nodes", [])
        
        if not articles:
            print("No articles found in Riot API response.")
            return None, None
            
        # The first item is always the newest published article
        latest_article = articles[0]
        title = latest_article.get("title")
        url_path = latest_article.get("url", {}).get("url")
        
        if not url_path:
            return None, None
            
        # Construct absolute link
        if url_path.startswith("/"):
            full_url = f"https://www.leagueoflegends.com{url_path}"
        else:
            full_url = url_path
            
        return full_url, title
    except Exception as e:
        print(f"Error checking API: {e}")
        return None, None

def extract_text_from_patch(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Failed to fetch content from patch page: {url}"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip away code elements that clutter raw text outputs
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.extract()
            
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        return f"Error extracting patch layout: {e}"

def main():
    # Keep directory paths robust
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    latest_url, patch_title = get_latest_lol_patch()
    if not latest_url:
        print("Could not retrieve the latest patch details.")
        return

    print(f"Latest Live Patch: {patch_title}")
    print(f"Target URL: {latest_url}")
    
    last_saved_url = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            last_saved_url = f.read().strip()
            
    if latest_url != last_saved_url:
        print("New patch detected! Cleaning text format...")
        
        # Pull text components
        text_output = extract_text_from_patch(latest_url)
        
        # Save the layout content directly to root output path
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(text_output)
            
        # Keep tracking marker up to date
        with open(HISTORY_FILE, "w") as f:
            f.write(latest_url)
            
        print(f"Successfully saved to {OUTPUT_FILE}")
    else:
        print("No new League of Legends updates found today.")

if __name__ == "__main__":
    main()
