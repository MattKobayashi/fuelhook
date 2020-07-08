function fuelAlert() {
  
  var props = PropertiesService.getScriptProperties();
  var webhook_url = ""
  
  // Get the current timestamp in seconds and add to end of URL (this forces Google to not use an old copy of the prices)
  var ts = Math.round((new Date()).getTime() / 1000);
  
  var resp = JSON.parse(UrlFetchApp.fetch("https://projectzerothree.info/api.php?format=json&t=" + ts).getContentText());
  var content = "";
  
  var last_u91 = props.getProperty("LAST_U91");
  var last_u95 = props.getProperty("LAST_U95");
  var last_u98 = props.getProperty("LAST_U98");
  var last_diesel = props.getProperty("LAST_DIESEL");
  
  // U91 price and location
  var u91_price = resp.regions[0].prices[1].price;
  var u91_loc = resp.regions[0].prices[1].suburb + ", " + resp.regions[0].prices[1].state;
  
  // U95 price and location
  var u95_price = resp.regions[0].prices[2].price;
  var u95_loc = resp.regions[0].prices[2].suburb + ", " + resp.regions[0].prices[2].state;
  
  // U98 price and location
  var u98_price = resp.regions[0].prices[3].price;
  var u98_loc = resp.regions[0].prices[3].suburb + ", " + resp.regions[0].prices[3].state;
  
  // Diesel price and location
  var diesel_price = resp.regions[0].prices[4].price;
  var diesel_loc = resp.regions[0].prices[4].suburb + ", " + resp.regions[0].prices[4].state;
  
  if (last_u91 != u91_price) {
    content += last_u91 < u91_price ? ":arrow_up:\t\t" : ":arrow_down:\t\t";
    content += ":fuelpump: U91\t\t:dollar: " + u91_price + "\t\t:map: " + u91_loc + "\n\n"
  }
  
  if (last_u95 != u95_price) {
    content += last_u95 < u95_price ? ":arrow_up:\t\t" : ":arrow_down:\t\t";
    content += ":fuelpump: U95\t\t:dollar: " + u95_price + "\t\t:map: " + u95_loc + "\n\n"
  }
  
  if (last_u98 != u98_price) {
    content += last_u98 < u98_price ? ":arrow_up:\t\t" : ":arrow_down:\t\t";
    content += ":fuelpump: U98\t\t:dollar: " + u98_price + "\t\t:map: " + u98_loc + "\n\n"
  }
  
  if (last_diesel != diesel_price) {
    content += last_diesel < diesel_price ? ":arrow_up:\t\t" : ":arrow_down:\t\t";
    content += ":fuelpump: Diesel\t\t:dollar: " + diesel_price + "\t\t:map: " + diesel_loc + "\n\n"
  }
  
  if (content.length > 0) {
    content += "Prices are correct as of " + new Date() + "\n\n";
    content += "@everyone";
    
    var options = {
      'method' : 'post',
      'contentType': 'application/json',
      'payload' : '{ "content": ' + JSON.stringify(content) + '}'
    };
    
    UrlFetchApp.fetch(webhook_url, options);
  }
  
  props.setProperty("LAST_U91", u91_price);
  props.setProperty("LAST_U95", u95_price);
  props.setProperty("LAST_U98", u98_price);
  props.setProperty("LAST_DIESEL", diesel_price);
  
}
