import os
import re
import requests


def update_knives_out_version():
    # Target download tracking link
    url = "https://adl.netease.com/d/g/knivesout/c/gwna"

    # Browser headers to trick the server into thinking we are an actual visitor
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    try:
        print(f"Fetching URL via Session: {url}")
        session = requests.Session()

        # Step 1: Hit the link and allow full handling
        response = session.get(url, headers=headers, allow_redirects=True)
        final_url = response.url

        # Step 2: If it didn't change from the original, look inside the HTML body 
        # NetEase often uses `<meta http-equiv="refresh" content="0;url=... ">` or JS scripts to redirect
        if "gwna" in final_url or ".exe" not in final_url:
            print("Redirect not caught in headers. Inspecting page body for links...")
            
            # Find any cdn executable link hidden inside quotes/scripts/meta tags
            urls_in_body = re.findall(r'(https?://[^\s"\'>]+\.exe[^\s"\'>]*)', response.text)
            if urls_in_body:
                final_url = urls_in_body[0]
            else:
                # Fallback: Sometimes they serve a JSON string or dynamic config block
                # Let's clean out escaping characters common in JS bodies (\/)
                cleaned_text = response.text.replace("\\/", "/")
                urls_in_body = re.findall(r'(https?://[^\s"\'>]+\.exe[^\s"\'>]*)', cleaned_text)
                if urls_in_body:
                    final_url = urls_in_body[0]

        print(f"Resolved to final URL: {final_url}")

        # Step 3: Break down the filename
        filename = final_url.split("/")[-1].split("?")[0]

        if "-setup.exe" in filename:
            version_string = filename.replace("-setup.exe", "")
        else:
            # Fallback regex matching string structure
            match = re.search(r"([\w\.-]+-overseas-[\d\.]+)", filename)
            version_string = match.group(1) if match else filename

        print(f"Extracted Version String: {version_string}")

        # Fallback security check: if parsing completely fails, don't break the original file
        if version_string == "gwna" or not version_string:
            raise ValueError("Failed to extract the direct download link from NetEase.")

        # Step 4: Write out to file
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
