import json
import re
import subprocess
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_FILE = os.path.join(SCRIPT_DIR, "profiles.json")
SEEN_FILE = os.path.join(SCRIPT_DIR, "seen.json")
NEW_ITEMS_FILE = os.path.join(SCRIPT_DIR, "new_items.json")

MAX_POSTS = 10
MAX_COMMENTS = 20
RECENCY_DAYS = 14  # only surface comments posted within this many days


def days_ago(ago_str):
    s = ago_str.lower().split("•")[0].strip()
    if any(w in s for w in ("just now", "now", "moment")):
        return 0
    m = re.search(r"(\d+)\s*(second|minute|hour|day|week|month|year)", s)
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    if unit.startswith(("second", "minute", "hour")):
        return 0
    if unit.startswith("day"):
        return n
    if unit.startswith("week"):
        return n * 7
    if unit.startswith("month"):
        return n * 30
    if unit.startswith("year"):
        return n * 365
    return None


def is_recent(ago_str):
    d = days_ago(ago_str)
    return d is None or d <= RECENCY_DAYS


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return {"posts": [], "comments": []}
    with open(SEEN_FILE) as f:
        return json.load(f)


def apify_call(actor, input_data):
    result = subprocess.run(
        ["apify", "call", actor, f"--input={json.dumps(input_data)}"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if "datasets/" in line:
            dataset_id = line.strip().split("datasets/")[1].split()[0]
            return fetch_dataset(dataset_id)
    return []


def fetch_dataset(dataset_id):
    result = subprocess.run(
        ["apify", "datasets", "get-items", dataset_id, "--format=json"],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return json.loads(result.stdout)


def fetch_posts(profile_url):
    print("  posts ...", flush=True)
    return apify_call("harvestapi/linkedin-profile-posts", {
        "profileUrls": [profile_url],
        "maxPosts": MAX_POSTS
    })


def fetch_comments(profile_url):
    print("  comments ...", flush=True)
    return apify_call("unseenuser/LinkedIn-user-comments-reactions", {
        "profiles": [profile_url]
    })


def main():
    with open(PROFILES_FILE) as f:
        profiles = json.load(f)

    seen = load_seen()
    seen_post_ids = set(seen.get("posts", []))
    seen_comment_ids = set(seen.get("comments", []))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'━'*50}", flush=True)
    print(f"SIGNAL MONITOR — {now}", flush=True)
    print(f"Fetching from {len(profiles)} profiles...", flush=True)
    print(f"{'━'*50}\n", flush=True)

    new_posts = []
    new_comments = []

    for profile_url in profiles:
        name = profile_url.rstrip("/").split("/in/")[1]
        print(f"[{name}]", flush=True)

        posts = fetch_posts(profile_url)
        for p in posts:
            if p.get("id") and p["id"] not in seen_post_ids:
                new_posts.append({
                    "type": "post",
                    "id": p["id"],
                    "name": p.get("author", {}).get("name", name),
                    "ago": p.get("postedAt", {}).get("postedAgoText", ""),
                    "text": p.get("content", "").strip(),
                    "url": p.get("linkedinUrl", "")
                })

        raw_comments = fetch_comments(profile_url)
        recent = [c for c in raw_comments if is_recent(c.get("created_at", {}).get("relative", ""))]
        for c in recent[:MAX_COMMENTS]:
            if c.get("comment_urn") and c["comment_urn"] not in seen_comment_ids:
                new_comments.append({
                    "type": "comment",
                    "id": c["comment_urn"],
                    "name": c.get("commenter", {}).get("name", name),
                    "ago": c.get("created_at", {}).get("relative", ""),
                    "text": c.get("comment_text", "").strip(),
                    "url": c.get("comment_link", "")
                })

        print(f"  → {len(posts)} posts, {len(recent[:MAX_COMMENTS])} comments (last {RECENCY_DAYS} days)\n", flush=True)

    total_new = len(new_posts) + len(new_comments)
    print(f"{'━'*50}", flush=True)
    print(f"New items to filter: {len(new_posts)} posts, {len(new_comments)} comments ({total_new} total)", flush=True)
    print(f"{'━'*50}\n", flush=True)

    with open(NEW_ITEMS_FILE, "w") as f:
        json.dump({"posts": new_posts, "comments": new_comments}, f, indent=2)

    for p in new_posts:
        seen_post_ids.add(p["id"])
    for c in new_comments:
        seen_comment_ids.add(c["id"])

    seen["posts"] = list(seen_post_ids)
    seen["comments"] = list(seen_comment_ids)
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, indent=2)

    if total_new == 0:
        print("No new items. Nothing to filter.")
    else:
        print(f"new_items.json written. {total_new} items ready for relevance filter.")


if __name__ == "__main__":
    main()
