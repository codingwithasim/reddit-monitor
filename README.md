# 🤖 Reddit Coding Opportunity Monitor

A lightweight, fully local Python script that monitors Reddit for **coding-related freelance and job opportunities** and delivers intelligent alerts to Telegram.

Designed to surface real, paid opportunities — filtering out noise like free advice requests, homework help, internships, and low-quality posts.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 Smart detection | Intent + commercial signal analysis to find real opportunities |
| 🔥 Priority alerts | High-value posts flagged with 🔥 emoji |
| 🚫 Noise filtering | Negative keyword filter blocks spam and irrelevant posts |
| 📬 Telegram notifications | Instant alerts sent directly to your phone |
| 🧠 Deduplication | Remembers seen posts, no repeat notifications |
| ⚙️ Easy config | Single `config.json` file for all settings |
| 🔒 Free & local | No paid APIs, only a Telegram bot token required |

---

## 📁 Project Structure

```
reddit_monitor/
├── monitor.py          # Main monitoring script
├── config.json         # Configuration (bot token, chat ID, subreddits, keywords)
├── run.sh              # Launch script
├── requirements.txt    # Python dependencies
├── seen.json           # Auto-generated, tracks processed posts
├── venv/               # Python virtual environment
└── README.md
```

---

## 🚀 Setup Instructions (Arch Linux)

### 1. Install Python

```bash
sudo pacman -Syu python python-pip
```

### 2. Create the Project Directory

```bash
mkdir ~/reddit_monitor && cd ~/reddit_monitor
```

### 3. Set Up Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Make the Run Script Executable

```bash
chmod +x run.sh
```

---

## ⚙️ Configuration

Edit `config.json` and fill in your Telegram credentials:

```json
{
  "telegram_bot_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID",
  "subreddits": ["forhire", "freelance", "slavelabour"],
  "poll_interval_seconds": 60
}
```

**Getting your credentials:**

1. **Bot Token**: Message [@BotFather](https://t.me/BotFather) on Telegram and create a new bot.
2. **Chat ID**: Send any message to your bot, then visit:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   Your chat ID will appear in the response JSON.

---

## 🔍 How It Works

Every 60 seconds the script:

1. Fetches new posts from selected subreddits
2. Checks for coding + hiring intent
3. Applies smart filters (commercial signals + negative filters)
4. Sends formatted alert to Telegram if it’s a good match
5. Marks the post as seen

---

## 📦 Requirements

`requirements.txt`:

```
requests==2.32.3
```

---

## ⚠️ Disclaimer

This tool uses Reddit's **public JSON API** (no authentication required). Please use it responsibly and respect Reddit's [API terms of service](https://www.reddit.com/wiki/api/).

---

> Made for personal use. Feel free to fork and customize! 🛠️