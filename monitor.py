import requests
import time
import json
import os
from datetime import datetime
import sys

# ===================== CONFIG =====================
SUBREDDITS = ["entrepreneur", "forhire", "smallbusiness"]
KEYWORDS = ["automation", "scraper", "website", "bot", "freelance", "hiring"]

# How often to check (seconds)
CHECK_INTERVAL = 60

# File to store seen post IDs (prevents duplicate alerts)
SEEN_FILE = "seen.json"

# User-Agent header (Reddit requires this)
HEADERS = {
    "User-Agent": "LocalRedditKeywordMonitor/1.0 (by /u/yourusername)"
}

# =================================================

def load_seen_posts():
    """Load previously seen post IDs from JSON file."""
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_seen_posts(seen):
    """Save seen post IDs to JSON file."""
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def fetch_new_posts(subreddit):
    """Fetch newest posts from a subreddit using Reddit's public JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=20"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()["data"]["children"]
        else:
            print(f"Error fetching r/{subreddit}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Request failed for r/{subreddit}: {e}")
        return []

def contains_keyword(text, keywords):
    """Case-insensitive keyword search."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)

def main():
    print("🚀 Reddit Keyword Monitor Started")
    print(f"Monitoring subreddits: {', '.join(SUBREDDITS)}")
    print(f"Keywords: {', '.join(KEYWORDS)}")
    print(f"Checking every {CHECK_INTERVAL} seconds...\n")
    
    seen = load_seen_posts()
    print(f"Loaded {len(seen)} previously seen posts.\n")
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Checking for new posts...")
            
            new_matches = 0
            
            for sub in SUBREDDITS:
                posts = fetch_new_posts(sub)
                
                for post_data in posts:
                    post = post_data["data"]
                    post_id = post["id"]
                    
                    # Skip if already seen
                    if post_id in seen:
                        continue
                    
                    title = post["title"]
                    author = post.get("author", "[deleted]")
                    url = f"https://reddit.com{post['permalink']}"
                    
                    # Check title and selftext for keywords
                    if (contains_keyword(title, KEYWORDS) or 
                        contains_keyword(post.get("selftext", ""), KEYWORDS)):
                        
                        print("\n" + "="*80)
                        print(f"🔍 MATCH FOUND in r/{sub}")
                        print(f"Title: {title}")
                        print(f"Author: u/{author}")
                        print(f"Link: {url}")
                        print("="*80 + "\n")
                        
                        new_matches += 1
                        seen.add(post_id)
            
            if new_matches == 0:
                print("No new matches.")
            else:
                print(f"Found {new_matches} new matching post(s).")
            
            save_seen_posts(seen)
            print(f"Next check in {CHECK_INTERVAL} seconds...\n")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped by user.")
            save_seen_posts(seen)
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()