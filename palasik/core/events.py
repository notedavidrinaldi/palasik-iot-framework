#Untuk logging & eksperimen
# palasik/core/events.py
import csv
import os
from datetime import datetime

LOG_FILE = "data/logs/trust_log.csv"

def log_event(ip, trust, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{timestamp[-8:]}] {ip} | trust={trust} | action={action}")

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["timestamp", "ip", "trust_score", "action"])

        writer.writerow([timestamp, ip, trust, action])

