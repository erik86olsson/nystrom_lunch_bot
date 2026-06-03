import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.koknystrom.se/dagens-lunch/"
TOPIC = os.environ["NTFY_TOPIC"]


def fetch_menu():

    html = requests.get(
        URL,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"}
    ).text

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n")

    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    dagar = {
        0: "Måndag",
        1: "Tisdag",
        2: "Onsdag",
        3: "Torsdag",
        4: "Fredag"
    }

    veckodag = dagar.get(datetime.today().weekday())

    if not veckodag:
        return "Ingen lunch idag (helg)."

    match = re.search(
        rf"{veckodag}.*?(?=(Måndag|Tisdag|Onsdag|Torsdag|Fredag|Priser:|$))",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        menu = match.group(0).strip()
        return menu[:1500]

    # fallback: ta dagens lunch-rutan
    start = text.find("Dagens lunch")

    if start >= 0:
        return text[start:start + 1200]

    return "Lunchmenyn kunde inte tolkas."


def send(msg):

    response = requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data=msg.encode("utf-8"),
        headers={
            "Title": "Kok Nystrom Lunch",
            "Priority": "4",
            "Tags": "fork_and_knife"
        },
        timeout=20
    )

    response.raise_for_status()


menu = fetch_menu()
send(menu)

print(menu)
