import os
import re
import requests


def update_knives_out_version():
    url = "https://adl.netease.com/d/g/knivesout/c/gwna"

    try:
        print(f"Fetching URL: {url}")
        # Use a user-agent so NetEase doesn't give a generic short response to python-requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, allow_redirects=True)

        # Look through history to find the actual .exe download link if response.url is masked
        final_url = response.url
        for resp in response.history:
            if ".exe" in resp.headers.get("Location", ""):
                final_url = resp.headers["Location"]
                break

        print(f"Resolved to final URL: {final_url}")

        # Clean the URL to extract the filename safely
        filename = final_url.split("/")[-1].split("?")[0]

        # Ensure we are actually grabbing the version string and not a slug like 'gwna'
        if "-setup.exe" in filename:
            version_string = filename.replace("-setup.exe", "")
        else:
            # Look for a pattern matching the version string format if the filename structure varies
            match = re.search(r"([\w\.-]+-overseas-[\d\.]+)", filename)
            version_string = match.group(1) if match else filename

        print(f"Extracted Version String: {version_string}")

        # Direct path safety check for GitHub Actions context
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
