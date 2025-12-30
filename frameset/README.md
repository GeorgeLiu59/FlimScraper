# Frameset Scrapers

Python scripts to download videos and images from Frameset.

## Scripts Overview
`frameset_video_scraper.py`:  Downloads motion content (videos/GIFs) (`.gif`)
`frameset_still_scraper.py`:  Downloads high-quality still images (`.png`)

---

## frameset_video_scraper.py

Downloads videos and GIFs from Frameset's CDN using metadata files.

### Setup

1. **Install dependencies:**
   ```bash
   pip install requests
   ```

2. **Get your authentication cookies:**
   - Go to https://frameset.app and log in
   - Open browser DevTools (F12) → Network tab
   - Make any API request (e.g., search)
   - Copy all cookies from the request headers

3. **Set cookies as environment variable:**
   ```bash
   export FRAMESET_COOKIE_STRING='cookie1=value1; cookie2=value2; ...'
   ```

### Configuration

Edit these variables in the script:

| Variable | Description | Default |
|----------|-------------|---------|
| `OUTPUT_FOLDER` | Download destination | `"OUTPUT FOLDER"` |
| `MAX_WORKERS` | Parallel download threads | `48` |
| `MOTION_METADATA_FILE` | Motion items metadata | `motion_metadata.json` |
| `FRAMES_METADATA_FILE` | Frame items metadata | `frames_metadata.json` |

### Usage

```bash
python frameset_video_scraper.py
```

### Notes

- Reads from `motion_metadata.json` by default
- Downloads from CloudFront CDN (`d13mryl9xv19vu.cloudfront.net`)
- Automatically checks token expiry before running
- Skips already-downloaded files

---

## frameset_still_scraper.py

Downloads high-quality PNG stills via Frameset's signed URL API.

### Setup

1. **Install dependencies:**
   ```bash
   pip install curl_cffi
   ```

2. **Update cookies in script:**
   Edit the `COOKIES` dictionary with your current session cookies from Frameset.

### Configuration

Edit these variables in the script:

| Variable | Description | Default |
|----------|-------------|---------|
| `METADATA_FILE` | Path to metadata JSON | `"PATH TO METADATA"` |
| `OUTPUT_FOLDER` | Download destination | `"OUTPUT FOLDER"` |
| `MAX_WORKERS` | Parallel download threads | `4` |

### Usage

```bash
python frameset_still_scraper.py
```

### How It Works

1. Loads image IDs from metadata file
2. Requests signed S3 URL from `frameset.app/api/image/{id}/download`
3. Downloads full-resolution PNG from signed URL
4. Handles rate limiting (429) with automatic retry

### Notes

- Uses `curl_cffi` to impersonate Chrome for anti-bot bypass
- Lower default workers (4) to avoid rate limiting
- Outputs `.png` files only

---

## Common Notes

- **Cookies expire periodically** — update them when requests start failing
- **Existing downloads are skipped** automatically
- Look up item info by searching for the ID in the metadata files
