#!/usr/bin/env python3

import requests
import json
import os
import copy
from time import strftime, localtime

# Define fuel types to check
fuelTypes = json.loads(os.environ.get("FUEL_TYPES"))

# Set the URL for the ProjectZeroThree API
apiURL = "https://projectzerothree.info/api.php?format=json"

# Create price data JSON file if it doesn't already exist
if (
    not os.path.isfile("data/priceData.json")
    or os.path.getsize("data/priceData.json") == 0
):
    blankPrice = {"E10": 0, "U91": 0, "U95": 0, "U98": 0, "Diesel": 0, "LPG": 0}
    with open("data/priceData.json", "w") as file:
        json.dump(blankPrice, file)
        file.close()

# Read last prices from JSON file
with open("data/priceData.json", "r") as file:
    priceDataFile = json.load(file)
    file.close()

# Get current price data from the API and parse the JSON
apiResponse = requests.post(apiURL, headers={"User-Agent": "FuelHook v2.4.0"})
priceDataAPI = json.loads(apiResponse.text)

# Get the last updated time from the API
lastUpdated = int(priceDataAPI["updated"])

# Create list of dicts with fuel price data from API
regionPref = str(os.environ.get("REGION"))
regionPrices = [
    copy.deepcopy(d) for d in priceDataAPI["regions"] if d["region"] == regionPref
][0]["prices"]

# Set the webhook URL and initialise content variable
webhookURL = str(os.environ.get("WEBHOOK_URL"))
content = ""

# Iterate on fuel types
for type in fuelTypes:

    # Set price and location variables
    price = float(next(item["price"] for item in regionPrices if item["type"] == type))
    loc = str(
        next(item["suburb"] for item in regionPrices if item["type"] == type)
        + ", "
        + next(item["state"] for item in regionPrices if item["type"] == type)
    )

    # Print the price and location data
    print("\nBest " + str(type) + " price: ", price, "\nLocated at: ", str(loc))

    # Add alert to content on price change
    if price != float(priceDataFile[type]):
        if price > float(priceDataFile[type]):
            if os.environ.get("WEBHOOK_TYPE") == "Discord":
                content += ":arrow_up:\t\t"
            if os.environ.get("WEBHOOK_TYPE") == "Telegram":
                content += "⬆️\t\t"
        else:
            if os.environ.get("WEBHOOK_TYPE") == "Discord":
                content += ":arrow_down:\t\t"
            if os.environ.get("WEBHOOK_TYPE") == "Telegram":
                content += "⬇️\t\t"
        if os.environ.get("WEBHOOK_TYPE") == "Discord":
            content += (
                ":fuelpump: "
                + str(type)
                + "\t\t:dollar: "
                + str(price)
                + "\t\t:map: "
                + str(loc)
                + "\n\n"
            )
        if os.environ.get("WEBHOOK_TYPE") == "Telegram":
            content += (
                "⛽️ "
                + str(type)
                + "\t\t💵 "
                + str(price)
                + "\t\t🗺️ "
                + str(loc)
                + "\n\n"
            )

    # Add price from API to price data file
    priceDataFile[type] = price

# Post any price changes to webhook
if content != "":
    content += (
        "Prices are correct as of "
        + strftime("%a %d %b %Y %H:%M:%S", localtime(lastUpdated))
    )
    if os.environ.get("WEBHOOK_TYPE") == "Discord":
        content += "\n@everyone"
        requests.post(webhookURL, data={"content": content})
    if os.environ.get("WEBHOOK_TYPE") == "Telegram":
        requests.post(webhookURL, params={
            "chat_id": int(os.environ.get("TELEGRAM_CHAT_ID")),
            "text": str(content)
            })

# Write the current price to the JSON file
with open("data/priceData.json", "w") as file:
    json.dump(priceDataFile, file)
    file.close()

# Print script completion to log
print(
    "\nScript executed successfully at: "
    + strftime("%a %d %b %Y %H:%M:%S", localtime())
    + "\n\n"
)
