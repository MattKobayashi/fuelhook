#!/usr/bin/env python3
import json
import os
import copy
from time import strftime, localtime
import requests

# Define fuel types to check
FUEL_TYPES = json.loads(os.environ.get("FUEL_TYPES"))

# Set the URL for the ProjectZeroThree API
API_URL = "https://projectzerothree.info/api.php?format=json"

# Create price data JSON file if it doesn't already exist
if (
    not os.path.isfile("data/priceData.json")
    or os.path.getsize("data/priceData.json") == 0
):
    BLANK_PRICE = {
        "E10": 0,
        "U91": 0,
        "U95": 0,
        "U98": 0,
        "Diesel": 0,
        "LPG": 0
    }
    with open("data/priceData.json", "w", encoding="utf-8") as file:
        json.dump(BLANK_PRICE, file)
        file.close()

# Read last prices from JSON file
with open("data/priceData.json", "r", encoding="utf-8") as file:
    PRICE_DATA_FILE = json.load(file)
    file.close()

# Get current price data from the API and parse the JSON
API_RESPONSE = requests.post(API_URL, headers={"User-Agent": "FuelHook v2.4.0"}, timeout=5)
PRICE_DATA_API = json.loads(API_RESPONSE.text)

# Get the last updated time from the API
LAST_UPDATED = int(PRICE_DATA_API["updated"])

# Create list of dicts with fuel price data from API
REGION_PREF = str(os.environ.get("REGION"))
REGION_PRICES = [
    copy.deepcopy(d)
    for d in PRICE_DATA_API["regions"]
    if d["region"] == REGION_PREF
][0]["prices"]

# Set the webhook URL and initialise content variable
WEBHOOK_URL = str(os.environ.get("WEBHOOK_URL"))
CONTENT = ""

# Iterate on fuel types
for FUEL_TYPE in FUEL_TYPES:

    # Set price and location variables
    PRICE = float(next(item["price"] for item in REGION_PRICES if item["type"] == FUEL_TYPE))
    LOC = str(
        next(item["suburb"] for item in REGION_PRICES if item["type"] == FUEL_TYPE)
        + ", "
        + next(item["state"] for item in REGION_PRICES if item["type"] == FUEL_TYPE)
    )

    # Print the price and location data
    print(
        "\nBest " + str(FUEL_TYPE) + " price: ",
        PRICE,
        "\nLocated at: ",
        str(LOC)
    )

    # Add alert to content on price change
    if PRICE != float(PRICE_DATA_FILE[FUEL_TYPE]):
        if PRICE > float(PRICE_DATA_FILE[FUEL_TYPE]):
            if os.environ.get("WEBHOOK_TYPE") == "Discord":
                CONTENT += ":arrow_up:\t\t"
            if os.environ.get("WEBHOOK_TYPE") == "Telegram":
                CONTENT += "⬆️\t\t"
        else:
            if os.environ.get("WEBHOOK_TYPE") == "Discord":
                CONTENT += ":arrow_down:\t\t"
            if os.environ.get("WEBHOOK_TYPE") == "Telegram":
                CONTENT += "⬇️\t\t"
        if os.environ.get("WEBHOOK_TYPE") == "Discord":
            CONTENT += (
                ":fuelpump: "
                + str(FUEL_TYPE)
                + "\t\t:dollar: "
                + str(PRICE)
                + "\t\t:map: "
                + str(LOC)
                + "\n\n"
            )
        if os.environ.get("WEBHOOK_TYPE") == "Telegram":
            CONTENT += (
                "⛽️ "
                + str(FUEL_TYPE)
                + "\t\t💵 "
                + str(PRICE)
                + "\t\t🗺️ "
                + str(LOC)
                + "\n\n"
            )

    # Add price from API to price data file
    PRICE_DATA_FILE[FUEL_TYPE] = PRICE

# Post any price changes to webhook
if CONTENT != "":
    CONTENT += (
        "Prices are correct as of "
        + strftime(
            "%a %d %b %Y %H:%M:%S",
            localtime(LAST_UPDATED)
        )
    )
    if os.environ.get("WEBHOOK_TYPE") == "Discord":
        CONTENT += "\n@everyone"
        requests.post(
            WEBHOOK_URL,
            data={
                "content": CONTENT
            },
            timeout=5
        )
    if os.environ.get("WEBHOOK_TYPE") == "Telegram":
        requests.post(
            WEBHOOK_URL,
            params={
                "chat_id": int(os.environ.get("TELEGRAM_CHAT_ID")),
                "text": str(CONTENT)
            }, timeout=5
        )

# Write the current price to the JSON file
with open("data/priceData.json", "w", encoding="utf-8") as file:
    json.dump(PRICE_DATA_FILE, file)
    file.close()

# Print script completion to log
print(
    "\nScript executed successfully at: "
    + strftime("%a %d %b %Y %H:%M:%S", localtime())
    + "\n\n"
)
