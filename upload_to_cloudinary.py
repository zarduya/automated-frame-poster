import os
import json
import time
from tqdm import tqdm
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# -------------- CONFIG --------------
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
import cloudinary

load_dotenv()  # loads CLOUDINARY_URL from .env

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
if not CLOUDINARY_URL:
    raise SystemExit("ERROR: CLOUDINARY_URL not found in .env")

# ✅ Parse CLOUDINARY_URL manually
url = urlparse(CLOUDINARY_URL)
cloud_name = url.hostname
api_key = url.username
api_secret = url.password

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=True
)

print(f"✅ Cloudinary configured for cloud: {cloud_name}")


LOCAL_FRAMES_FOLDER = "frames"          # where your JPEGs are
CLOUD_FOLDER = "frames_project"         # folder name in Cloudinary
PROGRESS_MAP_FILE = "uploaded_map.json" # mapping: filename -> uploaded url
OUTPUT_FILE = "uploaded_frames.json"    # (legacy list of urls; optional)

# -------------- Helper functions --------------
def load_progress():
    if os.path.exists(PROGRESS_MAP_FILE):
        try:
            with open(PROGRESS_MAP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_progress(mapping):
    with open(PROGRESS_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)

def save_urls_list(mapping):
    # optional: write simple list of URLs for other uses
    urls = list(mapping.values())
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2)

# -------------- Main upload loop --------------
def main():
 if not os.path.isdir(LOCAL_FRAMES_FOLDER):
    print(f"⚠️ No local frames folder found — skipping uploads.")
    return


    # load progress map (filename -> url)
    progress = load_progress()
    uploaded_count_before = len(progress)

    # gather all image files (jpg/jpeg)
    all_files = sorted([
        f for f in os.listdir(LOCAL_FRAMES_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg"))
    ])

    print(f"Total local frames found: {len(all_files)}")
    print(f"Already uploaded (from progress): {uploaded_count_before}")

    to_upload = [f for f in all_files if f not in progress]

    if not to_upload:
        print("Nothing to upload. All files already uploaded.")
        save_urls_list(progress)
        return

    print(f"Will upload {len(to_upload)} new files. Starting upload...")

    # upload with progress bar
    for filename in tqdm(to_upload, desc="Uploading"):
        local_path = os.path.join(LOCAL_FRAMES_FOLDER, filename)
        try:
            result = cloudinary.uploader.upload(
                local_path,
                folder=CLOUD_FOLDER,
                use_filename=True,
                unique_filename=False,
                overwrite=False,
                resource_type="image",
                timeout=120
            )
            url = result.get("secure_url") or result.get("url")
            if url:
                progress[filename] = url
                # save progress every N uploads to be safe (here every 10 files)
                if len(progress) % 10 == 0:
                    save_progress(progress)
                    save_urls_list(progress)
            else:
                print(f"Warning: upload succeeded but no URL returned for {filename}")

            # small sleep to be gentle on network/cloudinary for big batches
            time.sleep(0.05)

        except Exception as e:
            print(f"\nError uploading {filename}: {e}")
            # save progress before exiting so we can resume later
            save_progress(progress)
            save_urls_list(progress)
            raise SystemExit("Upload stopped due to an error. Fix error and rerun to resume.")

    # final save
    save_progress(progress)
    save_urls_list(progress)
    print(f"\n✅ Upload complete. Total uploaded: {len(progress)}")
    print(f"Saved mapping file: {PROGRESS_MAP_FILE}")
    print(f"Saved URL list file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
