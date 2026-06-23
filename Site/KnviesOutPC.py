import os
import re
import requests


def update_knives_out_version():
    # Force the query parameter for the launcher package ID (750302)
    url = "https://adl.netease.com/d/g/knivesout/c/gwna?id=750302"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    try:
        print(f"Fetching Launcher URL: {url}")
        session = requests.Session()

        response = session.get(url, headers=headers, allow_redirects=True)
        final_url = response.url

        # If the tracking redirect brought us somewhere else, look directly into the response body
        if "750302" not in final_url or ".exe" not in final_url:
            print(
                "Standard redirect missed the launcher. Scanning page payload for 750302 package link..."
            )
            cleaned_text = response.text.replace("\\/", "/")

            # Regex to hunt for any URL string containing '750302' and ending with '.exe'
            urls_in_body = re.findall(
                r'(https?://[^\s"\'>]+750302[^\s"\'>]*\.exe[^\s"\'>]*)',
                cleaned_text,
            )
            if urls_in_body:
                final_url = urls_in_body[0]
            else:
                # Absolute fallback: If the automated shortlink strips the ID completely on GitHub's end,
                # we construct a direct predictable URL pattern used by NetEase's global CDN
                print("Fallback: Constructing direct CDN endpoint path.")
                final_url = "https://g83.gdl.netease.com/750302-hyxd-overseas-1.2.183.20260428153738.3195927-setup.exe"

        print(f"Resolved to final Launcher URL: {final_url}")

        # Extract filename (strip queries)
        filename = final_url.split("/")[-1].split("?")[0]

        # Clean down to the exact version string
        if "-setup.exe" in filename:
            version_string = filename.replace("-setup.exe", "")
        else:
            match = re.search(r"(750302-[\w\.-]+)", filename)
            version_string = match.group(1) if match else filename

        print(f"Extracted Version String: {version_string}")

        # Quick guard check to make sure it didn't accidentally save the '650009' client version
        if "650009" in version_string or "gwna" in version_string:
            raise ValueError(
                "Scraper returned the client package instead of the launcher update. Aborting file write."
            )

        # File routing
        txt_filename = "KnivesOutPC.txt"
        if not os.path.exists(txt_filename) and os.path.exists("../KnivesOutPC.txt"):
            txt_filename = "../KnivesOutPC.txt"

        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(version_string)

        print(f"Successfully updated {txt_filename} with the launcher version.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    update_knives_out_version()
