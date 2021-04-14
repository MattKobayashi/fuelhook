# fuelhook

## How to run

```Shell
docker build -t --name fuelhook .

docker run -d --name fuelhook fuelhook
```

## Environment variables

- TZ - Sets the timezone for logs (uses tzdata format, e.g. "Australia/Brisbane". Defaults to UTC)
- REGION - the name of the region (or state), this is one of All, VIC, NSW, QLD, WA. On top of this, there is also All-2, VIC-2, NSW-2, QLD-2, WA-2, All-3, VIC-3, NSW-3, QLD-3, WA-3. These represent the 2nd and 3rd best prices for each respective region.
- WEBHOOK_URL - Sets the URL for your webhook (Discord-compatible, may work with other webhooks)
