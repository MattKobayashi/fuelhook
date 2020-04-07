var settings = {"regions":["All"],"prices":[["U95",500],["U98",500],["Diesel",500]]};

function myFunction() {
  // Reset data if the settings changed.
  var props = PropertiesService.getScriptProperties();
  var last_settings = props.getProperty("LAST_SETTINGS");
  if (last_settings == null || last_settings != JSON.stringify(settings)) {
    props.setProperty("LAST_PRICES", "[]");
  }
  props.setProperty("LAST_SETTINGS", JSON.stringify(settings));

  // Get the current timestamp in seconds and add to end of URL (this forces Google to not use an old copy of the prices).
  var ts = Math.round((new Date()).getTime() / 1000);
  var resp = JSON.parse(UrlFetchApp.fetch("https://projectzerothree.info/api.php?format=json&t=" + ts).getContentText());
  notifyPrices(resp, settings.regions, settings.prices);
}

function notifyPrices(obj, regions, prices) {
  var webhook_url = "https://discordapp.com/api/webhooks/614778623798280204/epoYdFR9VsJ9S2gvxqqX1cPkg2u_mJn69v_7NJv8J3Txw_nhr2so63gk56k-tnafbjsL";
  var best_prices = [];

  // Scan the response from the server for the matching regions and price points.
  for (var i = 0; i < obj.regions.length; i++) {
    for (var x = 0; x < regions.length; x++) {
      if (regions[x] == obj.regions[i].region) {
        for (var y = 0; y < obj.regions[i].prices.length; y++) {
          var price = obj.regions[i].prices[y];
          for (var z = 0; z < prices.length; z++) {
            if (prices[z][0] == price.type && price.price <= prices[z][1]) {
              best_prices.push([regions[x], price]);
              break;
            }
          }
        }
        break;
      }
    }
  }

  // Check that the found prices are actually new.
  var content = "";
  var props = PropertiesService.getScriptProperties();
  var last_prices = props.getProperty("LAST_PRICES");
  last_prices = last_prices == null ? [] : JSON.parse(last_prices);
  for (var i = 0; i < best_prices.length; i++) {
    best_prices[i][1].updated = obj.updated;

    var is_new = true;
    var old_price = null;
    // Search the old prices for a matching store.
    for (var x = 0; x < last_prices.length; x++) {
      if (last_prices[x][0] == best_prices[i][0] &&
          last_prices[x][1].type == best_prices[i][1].type) {
        var same_info = last_prices[x][1].name == best_prices[i][1].name &&
            last_prices[x][1].suburb == best_prices[i][1].suburb &&
            last_prices[i][1].state == best_prices[i][1].state;
        if (last_prices[i][1].price != best_prices[i][1].price) {
          old_price = last_prices[i][1];
        } else if (same_info) {
          is_new = false;
        }
      }
    }
    // If there is an old price, add an emoji to specify the trend.
    if (old_price) {
      content += old_price.price < best_prices[i][1].price ? ":arrow_up:\t" : ":arrow_down:\t";
    }
    // Write the store information
    content += ":fuelpump: " + best_prices[i][1].type + "\t:dollar: " + best_prices[i][1].price + "\t:map: ";
    content += best_prices[i][1].suburb + ", " + best_prices[i][1].state + "\n\n";
    // Note the previous price and how old it is
    if (old_price) {
      content += "Previously was " + old_price.price + " @ " + old_price.name + " (" + timeSince(new Date(old_price.updated * 1000)) + " ago) \n\n";
    }
  }

  // Save the current prices.
  props.setProperty("LAST_PRICES", JSON.stringify(best_prices));

  // Check there is anything to send.
  if (content.length > 0 && is_new == true) {
    content += "Prices are correct as of " + new Date(obj.updated * 1000) + " @everyone";
    // Make a POST request with a JSON payload.
    var options = {
      'method' : 'post',
      'contentType': 'application/json',
      // Convert the JavaScript object to a JSON string.
      'payload' : '{ "content": ' + JSON.stringify(content) + '}'
    };
    UrlFetchApp.fetch(webhook_url, options);
  }
}

function timeSince(date) {
  var seconds = Math.floor((new Date() - date) / 1000);
  var interval = Math.floor(seconds / 31536000);

  if (interval > 1) {
    return interval + " years";
  }
  interval = Math.floor(seconds / 2592000);
  if (interval > 1) {
    return interval + " months";
  }
  interval = Math.floor(seconds / 86400);
  if (interval > 1) {
    return interval + " days";
  }
  interval = Math.floor(seconds / 3600);
  if (interval > 1) {
    return interval + " hours";
  }
  interval = Math.floor(seconds / 60);
  if (interval > 1) {
    return interval + " minutes";
  }
  return Math.floor(seconds) + " seconds";
}
