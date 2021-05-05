import requests
import json
import os
from time import strftime, localtime

# Create price data JSON file if it doesn't already exist
if not os.path.isfile('data/priceData.json'):
    blankPrice = {"E10":0,"U91":0,"U95":0,"U98":0,"Diesel":0,"LPG":0}
    with open('data/priceData.json', 'w') as file:
        json.dump(blankPrice, file)
        file.close()

# Read last prices from JSON file
with open('data/priceData.json', 'r') as file:
    priceDataFile = json.load(file)
    file.close()

# Set the URL for the ProjectZeroThree API
apiURL = 'https://projectzerothree.info/api.php?format=json'

# Get current price data from the API and parse the JSON
apiResponse = requests.post(apiURL, headers={ 'User-Agent': 'FuelHook v2.1' })
priceDataAPI = json.loads(apiResponse.text)

# Get the prices and locations into variables
lastUpdated = int(priceDataAPI['updated'])
regionPref = int(os.environ.get('REGION'))

priceE10 = float(priceDataAPI['regions'][regionPref]['prices'][0]['price'])
locE10 = str(priceDataAPI['regions'][regionPref]['prices'][0]['suburb'] + ", " + priceDataAPI['regions'][regionPref]['prices'][0]['state'])

priceU91 = float(priceDataAPI['regions'][regionPref]['prices'][1]['price'])
locU91 = str(priceDataAPI['regions'][regionPref]['prices'][1]['suburb'] + ", " + priceDataAPI['regions'][regionPref]['prices'][1]['state'])

priceU95 = float(priceDataAPI['regions'][regionPref]['prices'][2]['price'])
locU95 = str(priceDataAPI['regions'][regionPref]['prices'][2]['suburb'] + ", " + priceDataAPI['regions'][regionPref]['prices'][2]['state'])

priceU98 = float(priceDataAPI['regions'][regionPref]['prices'][3]['price'])
locU98 = str(priceDataAPI['regions'][regionPref]['prices'][3]['suburb'] + ", " + priceDataAPI['regions'][regionPref]['prices'][3]['state'])

priceDiesel = float(priceDataAPI['regions'][regionPref]['prices'][4]['price'])
locDiesel = str(priceDataAPI['regions'][regionPref]['prices'][4]['suburb'] + ", " + priceDataAPI['regions'][regionPref]['prices'][4]['state'])

priceLPG = float(priceDataAPI['regions'][regionPref]['prices'][5]['price'])
locLPG = str(priceDataAPI['regions'][regionPref]['prices'][5]['suburb'] + ", " + priceDataAPI['regions'][regionPref]['prices'][5]['state'])

# Print the last updated time
print("Prices last updated at: ", strftime("%a %d %b %Y %H:%M:%S", localtime(lastUpdated)))

# Print the current prices
print("\nBest E10 price: ", priceE10, "\nLocated at: ", locE10)
print("\nBest U91 price: ", priceU91, "\nLocated at: ", locU91)
print("\nBest U95 price: ", priceU95, "\nLocated at: ", locU95)
print("\nBest U98 price: ", priceU98, "\nLocated at: ", locU98)
print("\nBest diesel price: ", priceDiesel, "\nLocated at: ", locDiesel)
print("\nBest LPG price: ", priceLPG, "\nLocated at: ", locLPG)

## Configure the webhook URL and post data
webhookURL = str(os.environ.get('WEBHOOK_URL'))
content = ""

# Alert on E10 change
if priceE10 != float(priceDataFile['E10']):
    if priceE10 > float(priceDataFile['E10']):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: E10\t\t:dollar: " + str(priceE10) + "\t\t:map: " + str(locE10) + "\n\n"

# Alert on U91 change
if priceU91 != float(priceDataFile['U91']):
    if priceU91 > float(priceDataFile['U91']):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: U91\t\t:dollar: " + str(priceU91) + "\t\t:map: " + str(locU91) + "\n\n"

# Alert on U95 change
if priceU95 != float(priceDataFile['U95']):
    if priceU95 > float(priceDataFile['U95']):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: U95\t\t:dollar: " + str(priceU95) + "\t\t:map: " + str(locU95) + "\n\n"

# Alert on U98 change
if priceU98 != float(priceDataFile['U98']):
    if priceU98 > float(priceDataFile['U98']):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: U98\t\t:dollar: " + str(priceU98) + "\t\t:map: " + str(locU98) + "\n\n"

# Alert on Diesel change
if priceDiesel != float(priceDataFile['Diesel']):
    if priceDiesel > float(priceDataFile['Diesel']):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: Diesel\t\t:dollar: " + str(priceDiesel) + "\t\t:map: " + str(locDiesel) + "\n\n"

# Alert on LPG change
if priceLPG != float(priceDataFile['LPG']):
    if priceLPG > float(priceDataFile['LPG']):
        content += ":arrow_up:\t\t"
    else:
        content += ":arrow_down:\t\t"
    content += ":fuelpump: LPG\t\t:dollar: " + str(priceLPG) + "\t\t:map: " + str(locLPG) + "\n\n"

if content != "":
    content += "Prices are correct as of " + strftime("%a %d %b %Y %H:%M:%S", localtime(lastUpdated)) + "\n@everyone"
    requests.post(webhookURL, data={ 'content': content })

# Update price data with current prices
priceDataFile['E10'] = priceE10
priceDataFile['U91'] = priceU91
priceDataFile['U95'] = priceU95
priceDataFile['U98'] = priceU98
priceDataFile['Diesel'] = priceDiesel
priceDataFile['LPG'] = priceLPG

# Write the current price to the JSON file
with open('/opt/fuelhook/data/priceData.json', 'w') as file:
    json.dump(priceDataFile, file)
    file.close()

# Print script completion to log
print("\nScript executed successfully at: " + strftime("%a %d %b %Y %H:%M:%S", localtime()) + "\n\n")
