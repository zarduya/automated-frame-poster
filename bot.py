import os
import json
import tempfile
import requests
import tweepy
import cloudinary
import cloudinary.api
import time

# === STARTUP CHECKS ===
print("✅ Starting bot... checking environment variables:")
print("API_KEY:", bool(os.getenv("API_KEY")))
print("ACCESS_TOKEN:", bool(os.getenv("ACCESS_TOKEN")))
print("CLOUDINARY_URL:", bool(os.getenv("CLOUDINARY_URL")))

# === TWITTER KEYS ===
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER = os.getenv("BEARER_TOKEN")

# === CLOUDINARY CONFIG ===
cloudinary.config(secure=True)

# === STATE TRACKING FILE ===
STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump({"last_posted_index": 0}, f)
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def setup_clients():
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        bearer_token=BEARER,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET,
    )
    return api_v1, client_v2


def get_cloudinary_frames():
    print("📡 Fetching frames from Cloudinary...")
    try:
        all_frames = []
        next_cursor = None
        while True:
            result = cloudinary.api.resources(
                type="upload",
                prefix="frames_project/",
                max_results=500,
                next_cursor=next_cursor,
            )
            all_frames.extend(result.get("resources", []))
            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break

        all_frames.sort(key=lambda x: x["public_id"])
        print(f"🔍 Total frames fetched: {len(all_frames)}")
        return [r["secure_url"] for r in all_frames]

    except Exception as e:
        print("❌ Error fetching Cloudinary resources:", e)
        return []


def post_frame(api_v1, client_v2, img_url, index, total):
    caption = f"They Call Him OG — Frame #{index + 1}/{total}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        img_data = requests.get(img_url).content
        tmp.write(img_data)
        tmp_path = tmp.name

    try:
        media = api_v1.media_upload(filename=tmp_path)
        client_v2.create_tweet(text=caption, media_ids=[media.media_id])
        print(f"✅ Posted frame {index + 1}/{total}")
    except Exception as e:
        print(f"❌ Error posting frame {index + 1}: {e}")
    finally:
        os.remove(tmp_path)


def post_batch_of_frames():
    frames = get_cloudinary_frames()
    if not frames:
        print("⚠️ No frames found in Cloudinary.")
        return

    total_frames = len(frames)
    state = load_state()
    start_index = state.get("last_posted_index", 0)

    if start_index >= total_frames:
        print("🎉 All frames have been posted successfully!")
        return

    api_v1, client_v2 = setup_clients()

    # Post 4 frames at a time
    for i in range(start_index, min(start_index + 4, total_frames)):
        print(f"⬇️ Downloading and posting frame {i + 1} ...")
        post_frame(api_v1, client_v2, frames[i], i, total_frames)
        time.sleep(10)  # 10 sec between tweets to stay safe

    # Save new state
    state["last_posted_index"] = min(start_index + 4, total_frames)
    save_state(state)
    print(f"✅ Batch complete. Next batch in 6 hours.")


if __name__ == "__main__":
    while True:
        post_batch_of_frames()
        print("⏳ Sleeping for 6 hours...")
        time.sleep(6 * 60 * 60)  # 6 hours
