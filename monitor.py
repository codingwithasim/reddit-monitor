import requests
import time
import json
import os
from datetime import datetime

# ===================== CONFIG =====================
CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from config.json"""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Error: {CONFIG_FILE} not found!")
        print("Please create the config.json file first.")
        exit(1)
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        # Validate essential fields
        if not config.get("telegram", {}).get("bot_token") or not config.get("telegram", {}).get("chat_id"):
            print("⚠️ Warning: Telegram bot_token or chat_id is missing in config.json")
        
        return config
    except Exception as e:
        print(f"❌ Error reading config.json: {e}")
        exit(1)

# Load config
config = load_config()

SUBREDDITS = config["subreddits"]
KEYWORDS = config["keywords"]
CHECK_INTERVAL = config["check_interval"]
TELEGRAM_BOT_TOKEN = config["telegram"]["bot_token"]
TELEGRAM_CHAT_ID = config["telegram"]["chat_id"]
USER_AGENT = config.get("user_agent", "LocalRedditKeywordMonitor/1.0")

HEADERS = {"User-Agent": USER_AGENT}

# =================================================

def send_telegram_message(text):
    """Send notification to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Telegram: {e}")
        return False

def load_seen_posts():
    if os.path.exists("seen.json"):
        try:
            with open("seen.json", "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_seen_posts(seen):
    with open("seen.json", "w") as f:
        json.dump(list(seen), f)

def fetch_new_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=20"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()["data"]["children"]
        else:
            print(f"Error {response.status_code} fetching r/{subreddit}")
            return []
    except Exception as e:
        print(f"Request failed for r/{subreddit}: {e}")
        return []

def contains_keyword(text, keywords):
    if not text:
        return False
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)

def main():
    print("🚀 Reddit Keyword Monitor Started (Config from config.json)")
    print(f"Subreddits : {', '.join(SUBREDDITS)}")
    print(f"Keywords   : {', '.join(KEYWORDS)}")
    print(f"Interval   : {CHECK_INTERVAL} seconds\n")
    
    seen = load_seen_posts()
    print(f"Loaded {len(seen)} previously seen posts.\n")
    
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking new posts...")
            
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
                    
                    if contains_keyword(title, KEYWORDS) or contains_keyword(post.get("selftext", ""), KEYWORDS):
                        
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
                        print("="*80)
                        
                        send_telegram_message(message)
                        seen.add(post_id)
            
            save_seen_posts(seen)
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