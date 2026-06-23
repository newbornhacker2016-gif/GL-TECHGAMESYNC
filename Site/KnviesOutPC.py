import os
import re
import requests

def update_knives_out_version():
    # Bypassing the shortlink and pointing directly to the global/regional distribution API
    # 750302 is your specific client package ID
    url = "https://adl.netease.com/d/g/knivesout/c/gwna?id=750302"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        print(f"Fetching targeted regional URL: {url}")
        session = requests.Session()
        
        # Explicitly hitting the endpoint
        response = session.get(url, headers=headers, allow_redirects=True)
        final_url = response.url

        # Check body if redirect didn't jump instantly in the cloud instance
        if "750302" not in final_url or ".exe" not in final_url:
            cleaned_text = response.text.replace("\\/", "/")
            # Look specifically for the 750302 package link in the response body
            urls_in_body = re.findall(r'(https?://[^\s"\'>]+750302[^\s"\'>]*\.exe[^\s"\'>]*)', cleaned_text)
            if urls_in_body:
                final_url = urls_in_body[0]

        print(f"Resolved to final URL: {final_url}")

        filename = final_url.split("/")[-1].split("?")[0]

        if "-setup.exe" in filename:
            version_string = filename.replace("-setup.exe", "")
        else:
            match = re.search(r"(750302-[\w\.-]+)", filename)
            version_string = match.group(1) if match else filename

        print(f"Extracted Version String: {version_string}")

        if "gwna" in version_string or "650009" in version_string:
            raise ValueError("Cloud routing returned fallback server. Aborting update to protect file.")

        txt_filename = "KnivesOutPC.txt"
        if not os.path.exists(txt_filename) and os.path.exists("../KnivesOutPC.txt"):
            txt_filename = "../KnivesOutPC.txt"

        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(version_string)

        print(f"Successfully updated {txt_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_knives_out_version()
