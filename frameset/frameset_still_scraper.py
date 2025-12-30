from curl_cffi import requests
import json
import time
import os
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
METADATA_FILE = Path("PATH TO METADATA")
OUTPUT_FOLDER = Path("OUTPUT FOLDER")
MAX_WORKERS = 4

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Headers: Extracted from your provided request log
HEADERS = {
    "authority": "frameset.app",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://frameset.app/search",
    "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

# Cookies: Supabase auth token (sb-...)
COOKIES = {
    "sessionId": "4b827273-5bd5-44c9-af6b-966ff309ca09",
    "sb-rxmhjspmurpimzyrvtzs-auth-token": "base64-eyJhY2Nlc3NfdG9rZW4iOiJleUpoYkdjaU9pSkZVekkxTmlJc0ltdHBaQ0k2SW1NNE16TmxNVFkzTFdNd056Y3ROR1JoTXkwNFpUYzJMVEJqTnpKaU1UWmhNR0k1TnlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaFlXd2lPaUpoWVd3eElpd2lZVzF5SWpwYmV5SnRaWFJvYjJRaU9pSndZWE56ZDI5eVpDSXNJblJwYldWemRHRnRjQ0k2TVRjMk5EWXlOekEyTm4xZExDSmhjSEJmYldWMFlXUmhkR0VpT25zaWNISnZkbWxrWlhJaU9pSmxiV0ZwYkNJc0luQnliM1pwWkdWeWN5STZXeUpsYldGcGJDSmRmU3dpWVhWa0lqb2lZWFYwYUdWdWRHbGpZWFJsWkNJNklqSTBNemxpTlRoaExXSTVOalF0TkdFM015MDVaV1E0TFRrM1pEVTNaRFJtWmpjNE9DSXNJbk4xWWlJNklqSmlOVEZtTTJRMExURXlOMlV0TkRjeFpTMDVNbVV3TFdabU1UYzJaVFExTkRJNVlTSXNJblZ6WlhKZmJXVjBZV1JoZEdFaU9uc2laR2x6Y0d4aGVWOXVZVzFsSWpvaVUybDVkV0Z1SUVObGJpSXNJbVZ0WVdsc0lqb2ljMk5sYmtCMWJXRnpjeTVsWkhVaUxDSmxiV0ZwYkY5MlpYSnBabWxsWkNJNmRISjFaU3dpYm1GdFpTSTZJbE5wZVhWaGJpQkRaVzRpTENKd2FHOXVaVjkyWlhKcFptbGxaQ0k2Wm1Gc2MyVXNJbk4xWWlJNklqSmlOVEZtTTJRMExURXlOMlV0TkRjeFpTMDVNbVV3TFdabU1UYzJaVFExTkRJNVlTSjlmUS5nRmJJdnhQZnhEM2gwWGxJWElzRWpyd0hTQy1YVXdlaEpoRkxBdHVERGJJdFZUaWxnNmRkeGpmcHItWEFMMmZTMkVua1h5YkZBcEk2LUgwdVVvSmh3ZyIsInRva2VuX3R5cGUiOiJiZWFyZXIiLCJleHBpcmVzX2luIjoxODAwLCJleHBpcmVzX2F0IjoxNzY2NjgyNDA4LCJyZWZyZXNoX3Rva2VuIjoibHJ6NnEzeXpqbXVyIiwidXNlciI6eyJpZCI6IjJiNTFmM2Q0LTEyN2UtNDcxZS05MmUwLWZmMTc2ZTQ1NDI5YSIsImF1ZCI6ImF1dGhlbnRpY2F0ZWQiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImVtYWlsIjoic2NlbkB1bWFzcy5lZHUiLCJlbWFpbF9jb25maXJtZWRfYXQiOiIyMDI1LTA5LTAyVDE5OjU2OjE2LjM5ODczN1oiLCJwaG9uZSI6IiIsImNvbmZpcm1lZF9hdCI6IjIwMjUtMDktMDJUMTk6NTY6MTYuMzk4NzM3WiIsInJlY292ZXJ5X3NlbnRfYXQiOiIyMDI1LTExLTIwVDIyOjE4OjQ2LjkxMjc4N1oiLCJsYXN0X3NpZ25faW5fYXQiOiIyMDI1LTA5LTExVDIyOjExOjA2LjI1MzQ4MloiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJkaXNwbGF5X25hbWUiOiJTaXl1YW4gQ2VuIiwiZW1haWwiOiJzY2VuQHVtYXNzLmVkdSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiU2l5dWFuIENlbiIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwic3ViIjoiMmI1MWYzZDQtMTI3ZS00NzFlLTkyZTAtZmYxNzZlNDU0MjlhIn0sImlkZW50aXRpZXMiOlt7ImlkZW50aXR5X2lkIjoiMWM1MjM1ZmEtNWYyMi00NTJiLTkzZTktYTVhY2MwNWE3N2QzIiwiaWQiOiIyYjUxZjNkNC0xMjdlLTQ3MWUtOTJlMC1mZjE3NmU0NTQyOWEiLCJ1c2VyX2lkIjoiMmI1MWYzZDQtMTI3ZS00NzFlLTkyZTAtZmYxNzZlNDU0MjlhIiwiaWRlbnRpdHlfZGF0YSI6eyJkaXNwbGF5X25hbWUiOiJTaXl1YW4gQ2VuIiwiZW1haWwiOiJzY2VuQHVtYXNzLmVkdSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IlNpeXVhbiBDZW4iLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6IjJiNTFmM2Q0LTEyN2UtNDcxZS05MmUwLWZmMTc2ZTQ1NDI5YSJ9LCJwcm92aWRlciI6ImVtYWlsIiwibGFzdF9zaWduX2luX2F0IjoiMjAyNS0wOS0wMlQxOTo1NjoxNi4zOTYwNDVaIiwiY3JlYXRlZF9hdCI6IjIwMjUtMDktMDJUMTk6NTY6MTYuMzk2MDkxWiIsInVwZGF0ZWRfYXQiOiIyMDI1LTA5LTAyVDE5OjU2OjE2LjM5NjA5MVoiLCJlbWFpbCI6InNjZW5AdW1hc3MuZWR1In1dLCJjcmVhdGVkX2F0IjoiMjAyNS0wOS0wMlQxOTo1NjoxNi4zOTA5NjNaIiwidXBkYXRlZF9hdCI6IjIwMjUtMTItMjVUMTY6MzY6NDguNDM5MDU2WiIsImlzX2Fub255bW91cyI6ZmFsc2V9fQ"
}

def download_image(item, index, total):
    image_id = item.get("id") or item.get("_id")
    if not image_id:
        logger.warning(f"[{index}/{total}] Skipping item without ID")
        return

    output_path = OUTPUT_FOLDER / f"{image_id}.png"
    if output_path.exists():
        logger.info(f"[{index}/{total}] Skipping {image_id} (already exists)")
        return

    api_url = f"https://frameset.app/api/image/{image_id}/download"

    try:
        # 1. Fetch Signed URL
        response = requests.get(
            api_url,
            headers=HEADERS,
            cookies=COOKIES,
            impersonate="chrome120",
            timeout=15
        )

        if response.status_code == 429:
            logger.warning(f"[{index}/{total}] Rate limited for {image_id}. Waiting...")
            time.sleep(30)
            return download_image(item, index, total)

        if response.status_code != 200:
            logger.error(f"[{index}/{total}] Failed to get signed URL for {image_id}: {response.status_code}")
            return

        data = response.json()
        if not data.get("success"):
            logger.error(f"[{index}/{total}] API reported failure for {image_id}")
            return

        signed_url = data["data"]["signedUrl"]

        # 2. Download Image
        img_response = requests.get(signed_url, impersonate="chrome120", timeout=60)
        
        if img_response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            logger.info(f"[{index}/{total}] Successfully downloaded {image_id}.png")
        else:
            logger.error(f"[{index}/{total}] Failed to download content for {image_id}: {img_response.status_code}")

    except Exception as e:
        logger.error(f"[{index}/{total}] Exception for {image_id}: {e}")

def main():
    # 1. Ensure Output Folder
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    # 2. Load Metadata
    if not METADATA_FILE.exists():
        logger.error(f"Metadata file not found: {METADATA_FILE}")
        return

    with open(METADATA_FILE, 'r') as f:
        try:
            items = json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse metadata: {e}")
            return

    if not isinstance(items, list):
        logger.error("Metadata is not a list")
        return

    # 3. Filter and Download
    logger.info(f"Loaded {len(items)} items. Starting downloads...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(download_image, item, i + 1, len(items)) for i, item in enumerate(items)]
        for future in as_completed(futures):
            # Results can be tracked here if needed
            pass

    logger.info("Finished batch download process.")

if __name__ == "__main__":
    main()