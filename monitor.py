import requests
import time
import json
import os
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===================== CONFIG =====================
SUBREDDITS = ["entrepreneur", "forhire", "smallbusiness"]
KEYWORDS = ["automation", "scraper", "website", "bot", "freelance", "hiring"]

# How often to check (seconds)
CHECK_INTERVAL = 60

# File to store seen post IDs (prevents duplicate alerts)
SEEN_FILE = "seen.json"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# User-Agent header (Reddit requires this)
HEADERS = {
    "User-Agent": "LocalRedditKeywordMonitor/1.0 (by /u/yourusername)"
}

# =================================================

def send_telegram_message(text):
    """Send notification to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured (skipping notification)")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Telegram error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False

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
    print("🚀 Reddit Keyword Monitor with Telegram Started")
    print(f"Subreddits: {', '.join(SUBREDDITS)}")
    print(f"Keywords: {', '.join(KEYWORDS)}\n")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Warning: Telegram is not configured. Check your .env file.\n")
    
    seen = load_seen_posts()
    print(f"Loaded {len(seen)} seen posts.\n")
    
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking...")
            
            for sub in SUBREDDITS:
                posts = fetch_new_posts(sub)
                
                for post_data in posts:
                    post = post_data["data"]
                    post_id = post["id"]
                    
                    if post_id in seen:
                        continue
                    
                    title = post["title"]
                    author = post.get("author", "[deleted]")
                    link = f"https://reddit.com{post['permalink']}"
                    
                    if (contains_keyword(title, KEYWORDS) or 
                        contains_keyword(post.get("selftext", ""), KEYWORDS)):
                        
                        # Prepare message
                        message = f"""
🔔 <b>New Match Found!</b>

📌 Subreddit: r/{sub}
👤 Author: u/{author}
🔖 Title: {title}
🔗 Link: {link}
                        """.strip()
                        
                        print("\n" + "="*80)
                        print(f"🔍 MATCH in r/{sub}")
                        print(f"Title: {title}")
                        print(f"Link: {link}")
                        print("="*80 + "\n")
                        
                        # Send to Telegram
                        send_telegram_message(message)
                        
                        seen.add(post_id)
            
            save_seen_posts(seen)
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped.")
            save_seen_posts(seen)
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()