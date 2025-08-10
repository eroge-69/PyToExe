import os
import random
import time
from datetime import datetime, timedelta, timezone
import json
import csv

import praw
from openai import OpenAI
from prawcore.exceptions import Forbidden, TooManyRequests

# --- Reddit API credentials ---
cfg_path = os.path.join(os.path.dirname(__file__), "credentials.json")
if not os.path.exists(cfg_path):
    raise FileNotFoundError(f"Missing credentials file: {cfg_path}")

with open(cfg_path, "r", encoding="utf-8") as f:
    config = json.load(f)

reddit = praw.Reddit(
    client_id=config["reddit"]["client_id"],
    client_secret=config["reddit"]["client_secret"],
    user_agent=config["reddit"]["user_agent"],
    username=config["reddit"]["username"],
    password=config["reddit"]["password"]
)

# --- OpenAI client ---
client = OpenAI(api_key=config["openai"]["api_key"])

# --- User Settings ---
nsfw_subreddits = config["subreddits"]["nsfw"]
sfw_subreddits = config["subreddits"]["sfw"]

# Media folders
image_folder = config["folders"]["image_folder"]
safe_image_folder = config["folders"]["safe_image_folder"]
video_folder = config["folders"]["video_folder"]
safe_video_folder = config["folders"]["safe_video_folder"]

# Rate settings
post_interval_min = timedelta(minutes=config["rate_settings"]["post_interval_min_minutes"])
post_interval_max = timedelta(minutes=config["rate_settings"]["post_interval_max_minutes"])
staffel_count = random.randint(
    config["rate_settings"]["staffel_count_min"],
    config["rate_settings"]["staffel_count_max"]
)

# NSFW vs SFW ratio
default_nsfw_probability = config["nsfw_probability"]


with open(os.path.join(os.path.dirname(__file__), "preferences.json"), "r") as f:
    prefs = json.load(f)

media_preferences = prefs["media_preferences"]
VIDEO_TO_REDGIF = prefs["VIDEO_TO_REDGIF"]
sfw_captions = prefs["sfw_captions"]


LOG_FILE = "posted_log.csv"



def append_post_log(media_name, source, subreddit, reddit_post_id=None, title=None):
    """
    Append a record to the post log.
    source = file path OR URL (like Redgif link)
    """
    try:
        log_file = "posted_log.csv"
        file_exists = os.path.isfile(log_file)

        with open(log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "media_name", "source", "subreddit", "reddit_post_id", "title"])

            writer.writerow([
                datetime.now().isoformat(),
                media_name,
                source,
                subreddit,
                reddit_post_id or "",
                title or ""
            ])
    except Exception as e:
        print(f"⚠️ Error writing to log: {e}")





# --- Helper functions ---

def sleep_with_checks(duration: timedelta):
    end = datetime.now(timezone.utc) + duration
    while datetime.now(timezone.utc) < end:
        remaining = (end - datetime.now(timezone.utc)).seconds
        time.sleep(min(300, remaining))


def get_description(sub: str, cat: str) -> str:
    prompt = (
        f"Write a flirty, teasing one-liner from a female's POV, talking directly to the viewer. "
        f"Keep it under 10 words, seductive and playful. "
        f"Subreddit: '{sub}', media type: '{cat}'. No hashtags or emojis."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate NSFW erotic descriptions, 1 sentence."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.9,
            max_tokens=20
        )
        return resp.choices[0].message.content.strip().strip('"').strip("'")
    except Exception:
        return "Error generating description"


def log_post(sub: str, media_file: str, desc: str, sfw: bool, is_video: bool):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    kind = "SFW" if sfw else "NSFW"
    media_type = "VIDEO" if is_video else "IMAGE"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {kind} {media_type} r/{sub} | {media_file} | {desc}\n")


def validate_folder(path: str, required_subdirs: bool = False):
    if not os.path.isdir(path):
        raise RuntimeError(f"Folder not found: {path}")
    if required_subdirs:
        subs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        if not subs:
            raise RuntimeError(f"No subdirectories in: {path}")

# Validate all media directories early
validate_folder(image_folder, required_subdirs=True)
validate_folder(safe_image_folder)
validate_folder(video_folder)
validate_folder(safe_video_folder)





# --- Main Loop ---
posts_in_staffel = 0

while True:
    # --- CHANGED: no redgifs_ready.csv anymore ---
    # Use the in-memory VIDEO_TO_REDGIF mapping (assumed defined elsewhere in your script).
    # Build a case-insensitive dict so the later exact_key / base_key lookup still works.
    try:
        redgif_ready_map_ci = {k.lower(): v for k, v in VIDEO_TO_REDGIF.items()}
    except NameError:
        # If VIDEO_TO_REDGIF isn't defined for some reason, behave like an empty map.
        redgif_ready_map_ci = {}
    # ------------------------------------------------

    # Decide if this post is NSFW or SFW (based on prefs or default probability)
    is_nsfw = None  # we'll set this below

    # Choose media type first: we'll pick media type and then filter subs accordingly

    # Pick NSFW or SFW first by global chance (if you want to respect pref's sfw overrides later)
    if random.random() < default_nsfw_probability:
        # NSFW post
        is_nsfw = True
        subs_pool = nsfw_subreddits
    else:
        # SFW post
        is_nsfw = False
        subs_pool = sfw_subreddits

    # Filter subs by those that actually exist in media_preferences to avoid errors
    subs_pool = [sub for sub in subs_pool if sub in media_preferences]

    if not subs_pool:
        print("⚠️ No subreddits available for this NSFW/SFW choice. Retrying...")
        continue

    # For each subreddit in the pool, check allowed media types based on prefs and NSFW status
    # Create a mapping of sub -> allowed media types (image/video/both)
    sub_allowed_media = {}
    for sub in subs_pool:
        pref = media_preferences.get(sub, {
            "type": "both",
            "sfw": None,
            "image_categories": [],
            "video_categories": []
        })
        # Determine actual NSFW status for this subreddit (pref can override)
        actual_nsfw = not pref["sfw"] if pref["sfw"] is not None else is_nsfw

        if actual_nsfw != is_nsfw:
            # Skip if NSFW/SFW mismatch
            continue

        allowed = []
        if not actual_nsfw:
            allowed = ["image"]  # SFW only images
        else:
            if pref["type"] in ("both", "image"):
                allowed.append("image")
            if pref["type"] in ("both", "video"):
                allowed.append("video")

        if allowed:
            sub_allowed_media[sub] = allowed

    if not sub_allowed_media:
        print(f"⚠️ No subreddits allow any media type for {'NSFW' if is_nsfw else 'SFW'} posts. Retrying...")
        continue

    # Now randomly pick media type to post (from all allowed media types available)
    all_allowed_media = [media for allowed in sub_allowed_media.values() for media in allowed]
    media_type = random.choice(all_allowed_media)
    is_video = (media_type == "video")

    # Now pick only subs that allow this media type
    candidate_subs = [sub for sub, allowed in sub_allowed_media.items() if media_type in allowed]

    if not candidate_subs:
        print(f"⚠️ No subreddits allow media type {media_type} for {'NSFW' if is_nsfw else 'SFW'} posts. Retrying...")
        continue

    sub = random.choice(candidate_subs)

    pref = media_preferences.get(sub, {
        "type": "both",
        "sfw": None,
        "image_categories": [],
        "video_categories": []
    })

    # Select base folder and extensions based on media type and NSFW
    if is_video:
        base_folder = video_folder if is_nsfw else safe_video_folder
        categories = pref.get("video_categories", [])
        exts = (".mp4", ".mov", ".gif")
    else:
        base_folder = image_folder if is_nsfw else safe_image_folder
        categories = pref.get("image_categories", [])
        exts = (".jpg", ".jpeg", ".png", ".gif")

    # Gather candidates (files) from categories or base folder
    candidates = []
    if categories:
        for cat in categories:
            path = os.path.join(base_folder, cat)
            if os.path.isdir(path):
                candidates.extend(
                    os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(exts)
                )
    else:
        if os.path.isdir(base_folder):
            candidates = [
                os.path.join(base_folder, f) for f in os.listdir(base_folder) if f.lower().endswith(exts)
            ]
        else:
            candidates = []

    if not candidates:
        print(f"❌ No {media_type}s found for r/{sub}, skipping.")
        continue

    media_path = random.choice(candidates)
    media_name = os.path.basename(media_path)

    # Generate title based on NSFW/SFW and media_type
    title = get_description(sub, media_type) if is_nsfw else random.choice(sfw_captions)
    title = title.replace("?", "")

    # Posting logic
    try:
        print(f"📤 Posting {'NSFW' if is_nsfw else 'SFW'} {'VIDEO' if is_video else 'IMAGE'} to r/{sub} | {media_name}")

        if is_video:
            if is_nsfw:
                # Use Redgif prepared links for NSFW videos ONLY
                exact_key = media_name.lower()
                base_key = os.path.splitext(media_name)[0].lower()

                redgif_url = redgif_ready_map_ci.get(exact_key) or redgif_ready_map_ci.get(base_key)

                if not redgif_url:
                    print(f"❌ No prepared Redgif link found for {media_name} (checked in in-memory VIDEO_TO_REDGIF). Skipping.")
                    continue

                # try to submit the link, but handle "flair required" by fetching templates and retrying
                try:
                    post = reddit.subreddit(sub).submit(title=title, url=redgif_url, nsfw=True)
                except Exception as e:
                    err_str = str(e)
                    # Detect flair-required error text from Reddit
                    if "SUBMIT_VALIDATION_FLAIR_REQUIRED" in err_str or ("flair" in err_str and "required" in err_str.lower()):
                        print(f"⚠️ r/{sub} requires post flair. Attempting to fetch flair templates and retry...")
                        # Try to get a flair template id (robust extraction)
                        flair_id = None
                        try:
                            templates = list(reddit.subreddit(sub).flair.link_templates)
                        except Exception as fetch_err:
                            templates = []
                            print(f"❌ Failed to fetch flair templates for r/{sub}: {fetch_err}")

                        # Try multiple possible attribute/key names for template id
                        for t in templates:
                            # support both dict-like and object-like templates
                            if isinstance(t, dict):
                                flair_id = t.get("id") or t.get("flair_template_id") or t.get("template_id")
                            else:
                                flair_id = getattr(t, "id", None) or getattr(t, "flair_template_id", None) or getattr(t, "template_id", None)
                            if flair_id:
                                break

                        if flair_id:
                            try:
                                print(f"🔧 Retrying with flair_id={flair_id}...")
                                post = reddit.subreddit(sub).submit(title=title, url=redgif_url, flair_id=flair_id, nsfw=True)
                                reddit_post_id = getattr(post, "id", None)
                                print(f"✅ Posted Redgif link for {media_name}: {redgif_url} (with flair)")
                                append_post_log(media_name, redgif_url, sub, reddit_post_id=reddit_post_id, title=title)
                                log_post(sub, media_name, title, sfw=not is_nsfw, is_video=is_video)
                                # success — continue to next iteration
                                continue
                            except Exception as e2:
                                print(f"❌ Failed to resubmit with flair for r/{sub}: {e2}")
                        else:
                            print(f"❌ No flair templates available or accessible for r/{sub}. Skipping post.")
                        # done handling flair-required, move on (skip this media)
                        continue
                    else:
                        # Other error — surface it as before
                        print(f"❌ Reddit error: {e}")
                        continue
                else:
                    # original successful path
                    reddit_post_id = getattr(post, "id", None)
                    print(f"✅ Posted Redgif link for {media_name}: {redgif_url}")
                    append_post_log(media_name, redgif_url, sub, reddit_post_id=reddit_post_id, title=title)
                    log_post(sub, media_name, title, sfw=not is_nsfw, is_video=is_video)
            else:
                # SFW videos: normal video upload
                reddit.subreddit(sub).submit_video(title=title, video_path=media_path)
                print("✅ Posted successfully.")
                log_post(sub, media_name, title, sfw=not is_nsfw, is_video=is_video)
        else:
            # Images: normal image upload
            reddit.subreddit(sub).submit_image(title=title, image_path=media_path, nsfw=is_nsfw)
            print("✅ Posted successfully.")
            log_post(sub, media_name, title, sfw=not is_nsfw, is_video=is_video)

    except TooManyRequests:
        print("⚠️ Reddit rate limit — backing off 1h")
        sleep_with_checks(timedelta(hours=1))
        continue
    except Forbidden:
        print(f"🚫 No permission in r/{sub}, removing subreddit")
        if is_nsfw:
            if sub in nsfw_subreddits:
                nsfw_subreddits.remove(sub)
        else:
            if sub in sfw_subreddits:
                sfw_subreddits.remove(sub)
        continue
    except Exception as e:
        print(f"❌ Reddit error: {e}")

    # Wait logic for posts in Staffel
    staffel_interval = timedelta(minutes=random.randint(1, 11))
    posts_in_staffel += 1

    if posts_in_staffel < staffel_count:
        wait = staffel_interval
    else:
        wait_seconds = random.randint(int(post_interval_min.total_seconds()), int(post_interval_max.total_seconds()))
        wait = timedelta(seconds=wait_seconds)
        posts_in_staffel = 0

    print(f"⏳ Sleeping for {wait.seconds // 60}m {wait.seconds % 60}s\n")
    sleep_with_checks(wait)
