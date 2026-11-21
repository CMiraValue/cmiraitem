# cmiraitem — C.MiraiItem weather feed

Data feed for C.MiraiItem VRChat gimmicks (Time Keeper DX weather panel and world clocks).

- `build.py` — fetches MET Norway Locationforecast for the cities in `cities.json` and writes `out/weather.txt`, `out/weather2.txt` and `out/index.html` (attribution).
- `.github/workflows/feed.yml` — scheduled hourly (at :23 + random wait). Copies `out/` into `feed/` and commits it to this repository; GitHub Pages serves it.
- Repository variable `FEED_UA` (optional): User-Agent with contact info — MET Norway requires it.
- GitHub may skip scheduled runs, so updates can be several hours apart. Read the hourly entries in `weather2.txt` for the current hour instead of trusting `temp`/`icon` to be current.

## Feed URLs

- v1: `https://cmiravalue.github.io/cmiraitem/feed/weather.txt` — used by Time Keeper DX. **Do not change its format.**
- v2: `https://cmiravalue.github.io/cmiraitem/feed/weather2.txt` — v1 + hourly forecast.

## Format v1 (`weather.txt`, UTF-8, one line per city)

```
CMI-WEATHER|1|<updated UTC>|<credit>
id|ja|en|ko|zh|utcOffsetMin|langHint|temp|icon|min|max|precipMm|daily
```

- `daily`: up to 8 entries `YYYYMMDD,weekday(0=Sun),icon,min,max` joined by `;` (local dates).
- `min`/`max`: today's range in local time. `precipMm`: next hour.
- icon: 0 clear, 1 partly, 2 cloudy, 3 fog, 4 rain, 5 sleet, 6 snow, 7 thunder, 8 clear night, 9 partly night. `x` = no data.

## Format v2 (`weather2.txt`)

Header `CMI-WEATHER|2|<updated UTC>|<credit>`. Each city line is the v1 line plus `|hourly`:

```
hourly = YYYYMMDDHH;temp,icon,precip;temp,icon,precip;...
```

- The first item is the UTC hour of the first entry; up to 48 consecutive hourly entries follow.
- Entry n (counting from 0) is for the UTC hour `YYYYMMDDHH` + n hours: temperature (°C) at the start of the hour, icon for that hour, precipitation (mm) in that hour.
- Empty when no hourly data is available — fall back to the v1 fields.
