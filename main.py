#!/usr/bin/env python3
import json
import os
import copy
from time import strftime, localtime
import requests
import apprise
from apprise import NotifyType

# Define fuel types to check
FUEL_TYPES = json.loads(os.environ.get("FUEL_TYPES"))

# Set the URL for the ProjectZeroThree API
API_URL = "https://projectzerothree.info/api.php?format=json"

# Create price data JSON file if it doesn't already exist
if (
    not os.path.isfile("data/priceData.json")
    or os.path.getsize("data/priceData.json") == 0
):
    BLANK_PRICE = {"E10": 0, "U91": 0, "U95": 0, "U98": 0, "Diesel": 0, "LPG": 0}
    with open("data/priceData.json", "w", encoding="utf-8") as file:
        json.dump(BLANK_PRICE, file)
        file.close()

# Read last prices from JSON file
with open("data/priceData.json", "r", encoding="utf-8") as file:
    PRICE_DATA_FILE = json.load(file)
    file.close()

# Get current price data from the API and parse the JSON
API_RESPONSE = requests.post(API_URL, headers={"User-Agent": "FuelHook v3"}, timeout=5)
PRICE_DATA_API = json.loads(API_RESPONSE.text)

# Get the last updated time from the API
LAST_UPDATED = int(PRICE_DATA_API["updated"])

# Create list of dicts with fuel price data from API
REGION_PREF = str(os.environ.get("REGION"))
REGION_PRICES = [
    copy.deepcopy(d) for d in PRICE_DATA_API["regions"] if d["region"] == REGION_PREF
][0]["prices"]

# Set the webhook URL and initialise content variable
APPRISE_URL = str(os.environ.get("APPRISE_URL"))
CONTENT = ""

# Configure Apprise and register the user-provided webhook
APPRISE = apprise.Apprise()
APPRISE.add(APPRISE_URL)

# Iterate on fuel types
for FUEL_TYPE in FUEL_TYPES:
    # Set price and location variables
    PRICE = float(
        next(item["price"] for item in REGION_PRICES if item["type"] == FUEL_TYPE)
    )
    LOC = str(
        next(item["suburb"] for item in REGION_PRICES if item["type"] == FUEL_TYPE)
        + ", "
        + next(item["state"] for item in REGION_PRICES if item["type"] == FUEL_TYPE)
    )

    # Print the price and location data
    print("\nBest " + str(FUEL_TYPE) + " price: ", PRICE, "\nLocated at: ", str(LOC))

    # Add alert to content on price change
    if PRICE != float(PRICE_DATA_FILE[FUEL_TYPE]):
        if PRICE > float(PRICE_DATA_FILE[FUEL_TYPE]):
            CONTENT += "⬆️\t\t"
        else:
            CONTENT += "⬇️\t\t"
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

# Post any price changes through Apprise
if CONTENT:
    CONTENT += "Prices are correct as of " + strftime(
        "%a %d %b %Y %H:%M:%S", localtime(LAST_UPDATED)
    )

    APPRISE.notify(
        title="Fuel Price Change",
        body=CONTENT,
        notify_type=NotifyType.INFO,
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
