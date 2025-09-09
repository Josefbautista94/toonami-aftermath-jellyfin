#!/usr/bin/env python3
import sys, os, json, urllib.request, urllib.parse, datetime, ssl

# -----------------------------
# Config
# -----------------------------
APP_CFGS = [
  "https://app.toonamiaftermath.com/config/index.json",
  "https://app.toonamiaftermath.com/config/toonamiaftermath.com/index.json",
]
API = "https://api.toonamiaftermath.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124 Safari/537.36")
ORIGIN = "https://www.toonamiaftermath.com"
REFERER = "https://www.toonamiaftermath.com/"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/var/lib/jellyfin/data/ToonamiAftermathGuide.xml"

# Channel logos (used by Jellyfin in the Guide column)
CHANNEL_LOGOS = {
    "ta.east":    "https://i.imgur.com/4qfad4o.gif",
    "ta.pacific": "https://i.imgur.com/4qfad4o.gif",
    "ta.movies":  "https://i.imgur.com/3HQ8mXb.png",
}

TLS_CTX = ssl.create_default_context()

# -----------------------------
# HTTP helpers
# -----------------------------
def http_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Origin": ORIGIN, "Referer": REFERER,
        "Accept": "application/json,text/plain,*/*",
    })
    with urllib.request.urlopen(req, timeout=25, context=TLS_CTX) as r:
        return json.load(r)

def find_schedule_names():
    for u in APP_CFGS:
        try:
            data = http_json(u)
        except Exception:
            continue
        chans = data.get("channels") or data.get("site", {}).get("channels")
        if not isinstance(chans, list):
            continue
        names = {}
        for ch in chans:
            nm = (ch.get("name") or "").strip()
            sched = (ch.get("scheduleName") or "").strip()
            if nm and sched:
                names[nm.lower()] = sched
        if names:
            return names
    return {}

def api_media(schedule_name, anchor_utc, count):
    qs = urllib.parse.urlencode({
        "scheduleName": schedule_name,
        "dateString": anchor_utc.strftime("%Y-%m-%dT%H:00:00.000Z"),
        "count": str(count),
    })
    url = f"{API}/media?{qs}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Origin": ORIGIN, "Referer": REFERER,
        "Accept": "application/json,text/plain,*/*",
    })
    with urllib.request.urlopen(req, timeout=25, context=TLS_CTX) as r:
        return json.load(r) or []

# -----------------------------
# Parsing + XML helpers
# -----------------------------
def parse_iso_z(s):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ","%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except Exception:
            pass
    return None

def esc(s):
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def title_of(it):
    info = it.get("info") or {}
    for k in ("fullname","title","name","programTitle","mediaTitle"):
        v = info.get(k) if k in info else it.get(k)
        if v: return str(v)
    return it.get("blockName") or "Toonami Aftermath"

def epi_bits(it):
    info = it.get("info") or {}
    st = info.get("episode") or it.get("episode") or None
    def as_int(x):
        try: return int(str(x).strip())
        except Exception: return None
    season = as_int(info.get("season") or it.get("season"))
    epnum  = as_int(info.get("episodeNumber") or it.get("episode_num") or it.get("episodeNo"))
    year   = as_int(info.get("year") or it.get("year"))
    return (st, season, epnum, year)

def rating_of(it):
    info = it.get("info") or {}
    v = info.get("rating") or it.get("rating")
    return str(v) if v else None

def poster_of(it):
    info = it.get("info") or {}
    v = info.get("image") or it.get("image")
    return str(v) if v else None

def desc_of(it):
    info = it.get("info") or {}
    for k in ("description","desc","synopsis","summary"):
        v = it.get(k) or info.get(k)
        if v: return str(v)
    parts=[]
    if it.get("blockName"): parts.append(f"Block: {it['blockName']}")
    if info.get("fullname"): parts.append(info["fullname"])
    st,season,epnum,year = epi_bits(it)
    if st: parts.append(f"Episode: {st}")
    se=[]
    if season is not None: se.append(f"S{season}")
    if epnum  is not None: se.append(f"E{epnum}")
    if se: parts.append("/".join(se))
    if year: parts.append(f"Year: {year}")
    score = it.get("score") or info.get("score")
    if score: parts.append(f"Score: {score}")
    return " • ".join(parts)

# -----------------------------
# Main
# -----------------------------
def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    cfg = find_schedule_names()
    main_sched = (cfg.get("toonami aftermath east") or
                  cfg.get("toonami aftermath est") or
                  cfg.get("toonami aftermath") or
                  "Toonami Aftermath EST")
    movies_sched = cfg.get("movies") or "Movies"

    channels = {
        "ta.east":    ("Toonami Aftermath (East)",    main_sched,   0),
        "ta.pacific": ("Toonami Aftermath (Pacific)", main_sched, 180),
        "ta.movies":  ("Toonami Movies",              movies_sched, 0),
    }

    anchor = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    COUNT = 96

    cache={}
    programmes=[]

    for chid,(disp,sched,delay) in channels.items():
        if sched not in cache:
            try: cache[sched]=api_media(sched, anchor, COUNT)
            except Exception: cache[sched]=[]
        items = cache[sched] or []
        for i,it in enumerate(items):
            start = parse_iso_z(it.get("startDate","") or it.get("start_time",""))
            if not start: continue
            if i+1<len(items):
                stop = parse_iso_z(items[i+1].get("startDate","") or items[i+1].get("start_time","")) or (start+datetime.timedelta(minutes=30))
            else:
                stop = start+datetime.timedelta(minutes=30)
            if delay:
                d=datetime.timedelta(minutes=delay); start+=d; stop+=d

            title = title_of(it)
            desc  = desc_of(it)
            sub_title, season, epnum, year = epi_bits(it)
            rating = rating_of(it)
            icon   = poster_of(it)  # programme poster (some clients use it)

            programmes.append((chid,start,stop,title,desc,sub_title,season,epnum,year,rating,icon))

    programmes.sort(key=lambda x:(x[0],x[1]))

    with open(OUT,"w",encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<tv generator-info-name="ta_epg_api.py">\n')

        # Write channel blocks (WITH channel icons for Jellyfin)
        for chid,(disp,_,_) in channels.items():
            f.write(f'  <channel id="{esc(chid)}">\n')
            f.write(f'    <display-name>{esc(disp)}</display-name>\n')
            logo = CHANNEL_LOGOS.get(chid)
            if logo:
                f.write(f'    <icon src="{esc(logo)}" />\n')
            f.write('  </channel>\n')

        # Write programme blocks (rich metadata)
        for (chid,start,stop,title,desc,sub_title,season,epnum,year,rating,icon) in programmes:
            f.write(f'  <programme start="{start.strftime("%Y%m%d%H%M%S")} +0000" ')
            f.write(f'stop="{stop.strftime("%Y%m%d%H%M%S")} +0000" channel="{esc(chid)}">\n')
            f.write(f'    <title lang="en">{esc(title)}</title>\n')
            if sub_title:
                f.write(f'    <sub-title lang="en">{esc(sub_title)}</sub-title>\n')

            # episode numbering
            if season is not None or epnum is not None:
                s0 = 0 if season is None else max(season-1,0)
                e0 = 0 if epnum  is None else max(epnum-1,0)
                f.write(f'    <episode-num system="xmltv_ns">{s0}.{e0}.</episode-num>\n')
                ons = ""
                if season is not None: ons += f"S{season}"
                if epnum  is not None: ons += f"E{epnum}" if season is not None else f"Ep {epnum}"
                if ons:
                    f.write(f'    <episode-num system="onscreen">{esc(ons)}</episode-num>\n')

            if year:
                f.write(f'    <date>{year}</date>\n')

            if rating:
                f.write('    <rating>\n')
                f.write(f'      <value>{esc(rating)}</value>\n')
                f.write('    </rating>\n')

            # Programme poster (some apps show this; Jellyfin ignores here but we keep it)
            if icon:
                f.write(f'    <icon src="{esc(icon)}" />\n')

            if desc:
                f.write(f'    <desc lang="en">{esc(desc)}</desc>\n')

            f.write('  </programme>\n')
        f.write('</tv>\n')

    print(f"Wrote {OUT} with {len(programmes)} programme entries.")
    if not programmes:
        print("WARNING: No programmes found (Movies may be empty).")

if __name__ == "__main__":
    main()

