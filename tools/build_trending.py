#!/usr/bin/env python3
"""Build trending.json from Bangladeshi news RSS feeds.

Runs on GitHub Actions every 30 minutes. Output (served by GitHub Pages):
  trending.json = {
    updated, sources:[{name,count}],
    top:      [article]  # stories covered by several papers, ranked
    latest:   [article]  # newest first
    breaking: [article]  # newest stories from the last few hours
  }
  article = {id,title,link,source,sourceIcon,image,summary,published,score}
"""
import hashlib, html, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlparse

import feedparser, requests

FEEDS = [
    # (source name, feed url) — first working URL per source is used
    ("প্রথম আলো", ["https://www.prothomalo.com/feed/", "https://www.prothomalo.com/stories.rss"]),
    ("বিডিনিউজ২৪", ["https://bangla.bdnews24.com/rss.xml", "https://bangla.bdnews24.com/?widgetName=rssfeed&widgetId=1151&getXmlFeed=true"]),
    ("কালের কণ্ঠ", ["https://www.kalerkantho.com/rss.xml"]),
    ("যুগান্তর", ["https://www.jugantor.com/feed/rss.xml", "https://www.jugantor.com/rss.xml"]),
    ("সমকাল", ["https://samakal.com/rss.xml", "https://samakal.com/feed"]),
    ("ইত্তেফাক", ["https://www.ittefaq.com.bd/rss.xml", "https://www.ittefaq.com.bd/feed"]),
    ("বাংলাদেশ প্রতিদিন", ["https://www.bd-pratidin.com/rss.xml"]),
    ("জাগো নিউজ", ["https://www.jagonews24.com/rss/rss.xml"]),
    ("বাংলা ট্রিবিউন", ["https://www.banglatribune.com/feed/", "https://www.banglatribune.com/rss.xml"]),
    ("ঢাকা পোস্ট", ["https://www.dhakapost.com/rss/rss.xml"]),
    ("রাইজিংবিডি", ["https://www.risingbd.com/rss/rss.xml"]),
    ("কালবেলা", ["https://www.kalbela.com/rss.xml", "https://www.kalbela.com/feed"]),
    ("দেশ রূপান্তর", ["https://www.deshrupantor.com/rss.xml"]),
    ("আজকের পত্রিকা", ["https://www.ajkerpatrika.com/feed", "https://www.ajkerpatrika.com/rss.xml"]),
    ("নয়া দিগন্ত", ["https://dailynayadiganta.com/rss/", "https://www.dailynayadiganta.com/rss.xml"]),
    ("ঢাকা টাইমস", ["https://www.dhakatimes24.com/rss.xml"]),
    ("সময় নিউজ", ["https://www.somoynews.tv/rss.xml"]),
    ("বিবিসি বাংলা", ["https://feeds.bbci.co.uk/bengali/rss.xml"]),
    ("ডয়চে ভেলে", ["https://rss.dw.com/rdf/rss-ben-all"]),
    ("The Daily Star", ["https://www.thedailystar.net/frontpage/rss.xml", "https://www.thedailystar.net/rss.xml"]),
    ("Dhaka Tribune", ["https://www.dhakatribune.com/feed/", "https://www.dhakatribune.com/rss.xml"]),
    ("The Financial Express", ["https://thefinancialexpress.com.bd/feed"]),
    ("New Age", ["https://www.newagebd.net/rss/rss.xml", "https://www.newagebd.net/rss.xml"]),
    ("Google News বাংলাদেশ", ["https://news.google.com/rss?hl=bn&gl=BD&ceid=BD:bn"]),
]
UA = {"User-Agent": "Mozilla/5.0 (compatible; CompleteNewsBot/1.0; +https://zahirul064.github.io/news_api/)"}
MAX_PER_SOURCE = 25
STOP = set("ও এ না কি যে এই সেই জন্য থেকে করে হয় হবে হলো নিয়ে দিয়ে বলে আর সঙ্গে সাথে মধ্যে পর আগে নতুন the a an of to in on for and is are with by at from as".split())


def clean(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text).strip()


def tokens(title):
    words = re.findall(r"[ঀ-৿]+|[A-Za-z]{3,}", title.lower())
    return {w for w in words if w not in STOP and len(w) > 1}


def image_of(e):
    for key in ("media_content", "media_thumbnail"):
        for m in e.get(key, []) or []:
            if m.get("url"):
                return m["url"]
    for l in e.get("links", []) or []:
        if l.get("type", "").startswith("image") and l.get("href"):
            return l["href"]
    m = re.search(r'<img[^>]+src="([^"]+)"', e.get("summary", "") or "")
    return m.group(1) if m else ""


def fetch(source):
    name, urls = source
    for url in urls:
        try:
            r = requests.get(url, headers=UA, timeout=20)
            if r.status_code != 200:
                continue
            feed = feedparser.parse(r.content)
            if not feed.entries:
                continue
            out = []
            for e in feed.entries[:MAX_PER_SOURCE]:
                title = clean(e.get("title"))
                link = e.get("link") or ""
                if not title or not link.startswith("http"):
                    continue
                src = name
                # Google News: "headline - Source"
                if "news.google.com" in url and " - " in title:
                    title, src = title.rsplit(" - ", 1)
                t = e.get("published_parsed") or e.get("updated_parsed")
                ts = int(time.mktime(t)) if t else int(time.time())
                host = urlparse(link).netloc
                if "news.google.com" in host and e.get("source", {}).get("href"):
                    host = urlparse(e["source"]["href"]).netloc
                out.append({
                    "id": hashlib.md5(link.encode()).hexdigest()[:12],
                    "title": title.strip(),
                    "link": link,
                    "source": src.strip(),
                    "sourceIcon": f"https://www.google.com/s2/favicons?domain={host}&sz=64",
                    "image": image_of(e),
                    "summary": clean(e.get("summary"))[:220],
                    "published": min(ts, int(time.time())),
                })
            print(f"OK   {name:22} {len(out):3}  {url}", file=sys.stderr)
            return name, out
        except Exception as ex:  # noqa: BLE001
            print(f"ERR  {name:22} {url}: {ex}", file=sys.stderr)
    print(f"FAIL {name}", file=sys.stderr)
    return name, []


def main(path="trending.json"):
    with ThreadPoolExecutor(12) as ex:
        results = list(ex.map(fetch, FEEDS))
    now = int(time.time())
    articles, seen = [], set()
    for _, items in results:
        for a in items:
            if a["link"] in seen or now - a["published"] > 3 * 86400:
                continue
            seen.add(a["link"])
            a["_t"] = tokens(a["title"])
            articles.append(a)

    # Trending score: how many OTHER sources ran a similar headline, plus freshness.
    for a in articles:
        cover = {a["source"]}
        for b in articles:
            if b is a or b["source"] in cover or not a["_t"] or not b["_t"]:
                continue
            overlap = len(a["_t"] & b["_t"]) / max(1, min(len(a["_t"]), len(b["_t"])))
            if overlap >= 0.5 and len(a["_t"] & b["_t"]) >= 2:
                cover.add(b["source"])
        hours = (now - a["published"]) / 3600
        a["score"] = round((len(cover) - 1) * 10 + max(0, 24 - hours) / 2 + (2 if a["image"] else 0), 2)

    # Top: best story per cluster (skip near-duplicates already chosen)
    top = []
    for a in sorted(articles, key=lambda x: (-x["score"], -x["published"])):
        if any(len(a["_t"] & t["_t"]) / max(1, min(len(a["_t"]), len(t["_t"]))) >= 0.5 for t in top):
            continue
        top.append(a)
        if len(top) >= 40:
            break
    latest = sorted(articles, key=lambda x: -x["published"])[:120]
    breaking = [a for a in latest if now - a["published"] <= 3 * 3600][:20]

    def pub(lst):
        return [{k: v for k, v in a.items() if k != "_t"} for a in lst]

    data = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [{"name": n, "count": len(i)} for n, i in results],
        "top": pub(top),
        "latest": pub(latest),
        "breaking": pub(breaking),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    ok = sum(1 for _, i in results if i)
    print(f"sources ok {ok}/{len(FEEDS)}  articles {len(articles)}  top {len(top)}  breaking {len(breaking)}", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
