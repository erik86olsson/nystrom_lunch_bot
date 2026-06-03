import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

TOPIC = os.environ["NTFY_TOPIC"]

URL = "https://www.koknystrom.se/dagens-lunch/"


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def fetch_menu():

    html = requests.get(
        URL,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    ).text

    soup = BeautifulSoup(html, "lxml")

    text = clean(soup.get_text("\n"))

    weekdays = {
        0: "Måndag",
        1: "Tisdag",
        2: "Onsdag",
        3: "Torsdag",
        4: "Fredag"
    }

    day = weekdays[datetime.today().weekday()]

    start = text.find(day)

    if start == -1:
        return "🍽️ Dagens lunch finns ännu inte publicerad."

    next_days = [
        "Måndag",
        "Tisdag",
        "Onsdag",
        "Torsdag",
        "Fredag"
    ]

    end = len(text)

    for d in next_days:
        pos = text.find(d, start + 20)
        if pos > start:
            end = min(end, pos)

    return text[start:end][:1200]


def send(msg):

    requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data=msg.encode("utf-8"),
        headers={
            "Title": "Kök Nyström",
            "Priority": "4"
        },
        timeout=20
    )


menu = fetch_menu()

send(menu)

print("Done")
