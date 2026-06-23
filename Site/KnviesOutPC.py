import os
import re
import requests


def update_knives_out_version():
    # Master distribution link
    url = "https://adl.netease.com/d/g/knivesout/c/gwna"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    try:
        print(f"Fetching master distribution link: {url}")
        session = requests.Session()

        # Follow redirects completely
        response = session.get(url, headers=headers, allow_redirects=True)
        final_url = response.url
        
        # Clean potential Javascript formatting backslashes out of the response body
        page_content = response.text.replace("\\/", "/")

        # Dynamic Extraction: Look for ANY package string pattern matching the launcher executable structure
        # This matches: digits + "-hyxd-overseas-" + version numbers + "-setup.exe"
        # Example target: 750302-hyxd-overseas-1.2.183.20260428153738.3195927-setup.exe
        launcher_match = re.search(r'([\d]+-hyxd-overseas-[\d\.]+-setup\.exe)', page_content)

        if launcher_match:
            filename = launcher_match.group(1)
            print(f"Found dynamic launcher pattern in payload: {filename}")
            version_string = filename.replace("-setup.exe", "")
        else:
            # Fallback: Parse from the redirected URL path if it managed to route correctly
            filename = final_url.split("/")[-1].split("?")[0]
            if "-hyxd-overseas-" in filename and "-setup.exe" in filename:
                version_string = filename.replace("-setup.exe", "")
            else:
                raise ValueError("Could not dynamically isolate the launcher package pattern from NetEase.")

        print(f"Extracted Version String: {version_string}")

        # Safety Guard: Ensure it didn't grab 'gwna' or empty values
        if version_string == "gwna" or not version_string:
            raise ValueError("Extraction parsed an invalid shortlink slug.")

        # File path resolution
        txt_filename = "KnivesOutPC.txt"
        if not os.path.exists(txt_filename) and os.path.exists("../KnivesOutPC.txt"):
            txt_filename = "../KnivesOutPC.txt"

        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(version_string)

        print(f"Successfully updated {txt_filename} with dynamic version.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    update_knives_out_version()
