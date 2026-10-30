import os
import time
from datetime import datetime, time as dtime
import requests
from bs4 import BeautifulSoup

URL = "https://fr.loropiana.com/en/shoes/woman/white-sole/summer-charms-walk-loafer-FAE5444_A760.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.environ.get("PUSHOVER_API_TOKEN")

def send_iphone_alarm(message_text):
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        print("Missing Pushover keys!")
        return

    payload = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": "🚨 LORO PIANA RESTOCK ALERT!",
        "message": message_text,
        "priority": 2,          # High Priority / Emergency Siren
        "sound": "siren",        # Continuous alarm sound
        "retry": 30,             # Repeats every 30 seconds
        "expire": 3600           # Keeps ringing up to 1 hour
    }
    try:
        requests.post("https://api.pushover.net/1/messages.json", data=payload, timeout=5)
    except Exception as e:
        print(f"Error sending alarm: {e}")

def check_stock():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=8)
        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.text, "html.parser")
        meta_avail = soup.find("meta", property="og:availability")
        if meta_avail and "instock" in meta_avail.get("content", "").lower():
            return True

        page_text = soup.get_text().lower()
        if "out of stock" not in page_text and "sold out" not in page_text:
            return True

        return False
    except Exception as e:
        return False

def run_window_checker():
    start_time = dtime(7, 0)   # 7:00 AM
    end_time = dtime(9, 0)     # 9:00 AM
    check_interval = 10        # Checks every 10 seconds

    print("Cloud Worker Running...")

    while True:
        now = datetime.now().time()
        
        if start_time <= now <= end_time:
            if check_stock():
                send_iphone_alarm(f"Item available now! Link: {URL}")
                time.sleep(300)
            else:
                time.sleep(check_interval)
        else:
            time.sleep(60)

if __name__ == "__main__":
    run_window_checker()
