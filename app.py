import requests
import json
import pickle
import os
from time import strftime, localtime, gmtime
from datetime import datetime

# Create pickle file if it doesn't already exist
if not os.path.isfile('data/lastprices.pkl'):
    blankPrice = ["0", "0", "0", "0", "0", "0"]
    with open('data/lastprices.pkl', 'wb') as file:
        pickle.dump(blankPrice, file)
        file.close()

# Read last prices from pickle file
with open('data/lastprices.pkl', 'rb') as file:
    e10LastPrice, u91LastPrice, u95LastPrice, u98LastPrice, dieselLastPrice, lpgLastPrice = pickle.load(file)
    file.close()

# Set the URL for the ProjectZeroThree API
apiUrl = 'https://projectzerothree.info/api.php?format=json'

# Get current price data from the API and parse the JSON
apiResponse = requests.post(apiUrl, headers={ 'User-Agent': 'FuelHook v2.0' })
priceData = json.loads(apiResponse.text)

# Get the prices and locations into variables
lastUpdated = int(priceData['updated'])

e10Price = float(priceData['regions'][int(os.environ.get('REGION'))]['prices'][0]['price'])
e10Location = str(priceData['regions'][int(os.environ.get('REGION'))]['prices'][0]['suburb'] + ", " + priceData['regions'][int(os.environ.get('REGION'))]['prices'][0]['state'])

u91Price = float(priceData['regions'][int(os.environ.get('REGION'))]['prices'][1]['price'])
u91Location = str(priceData['regions'][int(os.environ.get('REGION'))]['prices'][1]['suburb'] + ", " + priceData['regions'][int(os.environ.get('REGION'))]['prices'][1]['state'])

u95Price = float(priceData['regions'][int(os.environ.get('REGION'))]['prices'][2]['price'])
u95Location = str(priceData['regions'][int(os.environ.get('REGION'))]['prices'][2]['suburb'] + ", " + priceData['regions'][int(os.environ.get('REGION'))]['prices'][2]['state'])

u98Price = float(priceData['regions'][int(os.environ.get('REGION'))]['prices'][3]['price'])
u98Location = str(priceData['regions'][int(os.environ.get('REGION'))]['prices'][3]['suburb'] + ", " + priceData['regions'][int(os.environ.get('REGION'))]['prices'][3]['state'])

dieselPrice = float(priceData['regions'][int(os.environ.get('REGION'))]['prices'][4]['price'])
dieselLocation = str(priceData['regions'][int(os.environ.get('REGION'))]['prices'][4]['suburb'] + ", " + priceData['regions'][int(os.environ.get('REGION'))]['prices'][4]['state'])

lpgPrice = float(priceData['regions'][int(os.environ.get('REGION'))]['prices'][5]['price'])
lpgLocation = str(priceData['regions'][int(os.environ.get('REGION'))]['prices'][5]['suburb'] + ", " + priceData['regions'][int(os.environ.get('REGION'))]['prices'][5]['state'])

# Print the last updated time
print("Prices last updated at: ", strftime("%a %d %b %Y %H:%M:%S", localtime(lastUpdated)))

# Print the current prices
print("\nBest E10 price: ", e10Price, "\nLocated at: ", e10Location)
print("\nBest U91 price: ", u91Price, "\nLocated at: ", u91Location)
print("\nBest U95 price: ", u95Price, "\nLocated at: ", u95Location)
print("\nBest U98 price: ", u98Price, "\nLocated at: ", u98Location)
print("\nBest diesel price: ", dieselPrice, "\nLocated at: ", dieselLocation)
print("\nBest LPG price: ", lpgPrice, "\nLocated at: ", lpgLocation)

## Configure the Discord webhook URL and post data
webhookUrl = str(os.environ.get('DISCORD_WH_URL'))
content = ""

# Alert on E10 change
if e10Price != float(e10LastPrice):
    if e10Price > float(e10LastPrice):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: E10\t\t:dollar: " + str(e10Price) + "\t\t:map: " + str(e10Location) + "\n\n"

# Alert on U91 change
if u91Price != float(u91LastPrice):
    if u91Price > float(u91LastPrice):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: U91\t\t:dollar: " + str(u91Price) + "\t\t:map: " + str(u91Location) + "\n\n"

# Alert on U95 change
if u95Price != float(u95LastPrice):
    if u95Price > float(u95LastPrice):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: U95\t\t:dollar: " + str(u95Price) + "\t\t:map: " + str(u95Location) + "\n\n"

# Alert on U98 change
if u98Price != float(u98LastPrice):
    if u98Price > float(u98LastPrice):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: U98\t\t:dollar: " + str(u98Price) + "\t\t:map: " + str(u98Location) + "\n\n"

# Alert on Diesel change
if dieselPrice != float(dieselLastPrice):
    if dieselPrice > float(dieselLastPrice):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: Diesel\t\t:dollar: " + str(dieselPrice) + "\t\t:map: " + str(dieselLocation) + "\n\n"

# Alert on LPG change
if lpgPrice != float(lpgLastPrice):
    if lpgPrice > float(lpgLastPrice):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: LPG\t\t:dollar: " + str(lpgPrice) + "\t\t:map: " + str(lpgLocation) + "\n\n"

if content != "":
    content += "Prices are correct as of " + strftime("%a %d %b %Y %H:%M:%S", localtime(lastUpdated)) + "\n@everyone"
    requests.post(webhookUrl, data={ 'content': content })

# Write the current price to the pickle file
with open('data/lastprices.pkl', 'wb') as file:
    pickle.dump([e10Price, u91Price, u95Price, u98Price, dieselPrice, lpgPrice], file)
    file.close()

# Print script completion to log
print("\nScript executed successfully at: " + strftime("%a %d %b %Y %H:%M:%S", localtime()) + "\n\n")
