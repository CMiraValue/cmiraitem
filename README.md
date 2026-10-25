# cmiraiitem-feed (private)
 
Hourly data feed for C.MiraiItem VRChat gimmicks.
 
- `build.py` — fetches MET Norway Locationforecast for the cities in `cities.json` and writes `out/weather.txt` (+ `out/index.html` with attribution).
- `.github/workflows/feed.yml` — runs hourly (at :23 + random wait), publishes `out/` to the public Pages repo under `/feed/`.
- Required: repository variable `FEED_UA` (e.g. `CMiraiItemFeed/1.0 (+https://your-shop.booth.pm)` — MET Norway requires contact info), repository secret `DEPLOY_KEY` (private SSH key whose public key is a *write* deploy key on the Pages repo) and repository variable `PAGES_REPO` (e.g. `cmiraiitem/cmiraiitem.github.io`).
- Feed URL used by the gimmick: `https://<org>.github.io/feed/weather.txt`
 
Format (UTF-8, one line per city):
`CMI-WEATHER|1|<updated UTC>|<credit>` then `id|ja|en|ko|zh|utcOffsetMin|langHint|temp|icon|min|max|precipMm`
icon: 0 clear, 1 partly, 2 cloudy, 3 fog, 4 rain, 5 sleet, 6 snow, 7 thunder, 8 clear night, 9 partly night. `x` = no data.
