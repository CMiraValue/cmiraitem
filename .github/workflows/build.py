from zoneinfo import ZoneInfo
import json, os, time, random, gzip, urllib.request, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
UA = os.environ.get("FEED_UA") or "CMiraiItemFeed/1.0 (+https://github.com/cmiraiitem)"
CACHE = os.path.join(HERE, ".cache")
ICON = {"clearsky": 0, "fair": 1, "partlycloudy": 1, "cloudy": 2, "fog": 3, "lightrain": 4, "rain": 4, "heavyrain": 4, "lightrainshowers": 4, "rainshowers": 4, "heavyrainshowers": 4,
        "sleet": 5, "lightsleet": 5, "heavysleet": 5, "sleetshowers": 5, "snow": 6, "lightsnow": 6, "heavysnow": 6, "snowshowers": 6, "lightsnowshowers": 6, "heavysnowshowers": 6}
 
def icon(code):
    if not code: return 2
    base = code.split("_")[0]
    night = code.endswith("_night")
    if "thunder" in base: return 7
    k = ICON.get(base, 2)
    if night and k in (0, 1): k += 8
    return k
 
def fetch(lat, lon, key):
    os.makedirs(CACHE, exist_ok=True)
    meta_p = os.path.join(CACHE, key + ".meta"); body_p = os.path.join(CACHE, key + ".json")
    req = urllib.request.Request("https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=%.4f&lon=%.4f" % (lat, lon), headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    if os.path.exists(meta_p) and os.path.exists(body_p):
        m = json.load(open(meta_p))
        if m.get("expires", 0) > time.time(): return json.load(open(body_p))
        if m.get("lm"): req.add_header("If-Modified-Since", m["lm"])
    try:
        r = urllib.request.urlopen(req, timeout=30)
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip": raw = gzip.decompress(raw)
        exp = r.headers.get("Expires"); lm = r.headers.get("Last-Modified")
        exp_t = time.mktime(time.strptime(exp, "%a, %d %b %Y %H:%M:%S GMT")) - time.timezone if exp else time.time() + 1800
        open(body_p, "wb").write(raw); json.dump({"expires": exp_t, "lm": lm}, open(meta_p, "w"))
        return json.loads(raw)
    except urllib.error.HTTPError as e:
        if e.code == 304 and os.path.exists(body_p): return json.load(open(body_p))
        if e.code == 429: raise SystemExit("429 throttled, stop")
        raise
 
def summarize(d, tzmin):
    ts = d["properties"]["timeseries"]
    now = datetime.datetime.now(datetime.timezone.utc)
    cur = min(ts, key=lambda e: abs((datetime.datetime.fromisoformat(e["time"].replace("Z", "+00:00")) - now).total_seconds()))
    det = cur["data"]["instant"]["details"]
    nxt = cur["data"].get("next_1_hours") or cur["data"].get("next_6_hours") or {}
    code = nxt.get("summary", {}).get("symbol_code", "")
    pr = nxt.get("details", {}).get("precipitation_amount", 0.0)
    local_today = (now + datetime.timedelta(minutes=tzmin)).date()
    temps = [e["data"]["instant"]["details"]["air_temperature"] for e in ts if (datetime.datetime.fromisoformat(e["time"].replace("Z", "+00:00")) + datetime.timedelta(minutes=tzmin)).date() == local_today]
    lo = min(temps) if temps else det["air_temperature"]; hi = max(temps) if temps else det["air_temperature"]
    return "%d|%d|%d|%d|%.1f" % (round(det["air_temperature"]), icon(code), round(lo), round(hi), pr)
 
def main():
    cities = json.load(open(os.path.join(HERE, "cities.json")))
    os.makedirs(OUT, exist_ok=True)
    lines = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for c in cities:
        key, ko, ja, en, zh, lat, lon, tzname, lang = c
        tz = int(now.astimezone(ZoneInfo(tzname)).utcoffset().total_seconds() // 60)
        try:
            s = summarize(fetch(lat, lon, key), tz)
        except SystemExit:
            raise
        except Exception as e:
            print("skip", key, e); s = "x|x|x|x|x"
        lines.append("%s|%s|%s|%s|%s|%d|%s|%s" % (key, ja, en, ko, zh, tz, lang, s))
        time.sleep(0.3)
    head = "CMI-WEATHER|1|%s|Data from MET Norway (CC BY 4.0)" % now.strftime("%Y-%m-%dT%H:%MZ")
    txt = head + "\n" + "\n".join(lines) + "\n"
    open(os.path.join(OUT, "weather.txt"), "w", encoding="utf-8").write(txt)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write("<!doctype html><meta charset=utf-8><title>C.MiraiItem data</title><p>C.MiraiItem world gimmick data feed. Weather data from <a href='https://www.met.no/en'>MET Norway</a> (CC BY 4.0), processed.</p>")
    print("ok", len(lines))
 
if __name__ == "__main__":
    main()
