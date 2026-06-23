import os
import re
import requests


def update_knives_out_version():
    url = "https://adl.netease.com/d/g/knivesout/c/gwna"

    try:
        # 1. Send a request that automatically follows redirects
        print(f"Fetching URL: {url}")
        response = requests.get(url, allow_redirects=True)
        final_url = response.url
        print(f"Resolved to final URL: {final_url}")

        # 2. Extract the file name from the URL path
        # Example URL: https://g83.gdl.netease.com/750302-hyxd-overseas-1.2.183.20260428153738.3195927-setup.exe?key1=...
        # This splits the URL by '/' and takes the last part, then splits by '?' to discard parameters
        filename = final_url.split("/")[-1].split("?")[0]

        # 3. Strip the '-setup.exe' suffix to extract the exact version string
        if filename.endswith("-setup.exe"):
            version_string = filename.replace("-setup.exe", "")
        else:
            # Fallback regex just in case the extension format shifts slightly
            match = re.search(r"([\w\.-]+)-setup\.exe", filename)
            version_string = match.group(1) if match else filename

        print(f"Extracted Version String: {version_string}")

        # 4. Save to KnivesOutPC.txt (navigating up or using relative paths)
        # Assuming the script runs from the repository root or 'Site/' directory
        txt_filename = "KnivesOutPC.txt"

        # If running from inside 'Site/', look for the file in the parent directory
        if not os.path.exists(txt_filename) and os.path.exists("../KnivesOutPC.txt"):
            txt_filename = "../KnivesOutPC.txt"

        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(version_string)

        print(f"Successfully successfully updated {txt_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    update_knives_out_version()
