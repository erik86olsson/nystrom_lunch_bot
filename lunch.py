import requests
from bs4 import BeautifulSoup
from datetime import datetime
from base64 import b64encode
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
        headers={"User-Agent": "Mozilla/5.0"}
    ).text

    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text("\n")

    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    weekdays = {
        0: "Måndag",
        1: "Tisdag",
        2: "Onsdag",
        3: "Torsdag",
        4: "Fredag"
    }

    day = weekdays.get(datetime.today().weekday())

    if not day:
        return "🍽️ Ingen lunch idag"

    start = text.find(day)

    if start == -1:
        return "🍽️ Dagens lunch finns ännu inte publicerad."

    days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]

    end = len(text)

    for d in days:
        pos = text.find(d, start + 20)

        if pos > start:
            end = min(end, pos)

    menu = text[start:end]

    categories = [
        "Husman",
        "Världen",
        "Fisk",
        "Vego"
    ]

    result = [f"{day}\n"]
    icons = {
    "Husman": "🏠",
    "Världen": "🌍",
    "Fisk": "🐟",
    "Vego": "🍃"
}
    for i, category in enumerate(categories):

        pattern = (
            rf"{category}(.*?)(?="
            + "|".join(categories[i + 1:] + ["$"])
            + ")"
        )

        match = re.search(
            pattern,
            menu,
            re.DOTALL
        )

        if match:

            dish = clean(match.group(1))

result.append(
    f"\n{icons[category]} {category}\n{dish}"
)

    return "\n".join(result)


def send(msg):

    title = "Kök Nyström Lunch"

    encoded_title = (
        "=?UTF-8?B?"
        + b64encode(title.encode("utf-8")).decode()
        + "?="
    )

    response = requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data=msg.encode("utf-8"),
        headers={
            "Title": encoded_title,
            "Priority": "4",
            "Tags": "fork_and_knife"
        },
        timeout=20
    )

    response.raise_for_status()


menu = fetch_menu()

print(menu)

send(menu)
