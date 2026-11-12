"""Check every list the app reads, so a typo on GitHub is caught right away.

Runs on every push (counts.yml). If something is wrong the workflow turns red
and GitHub e-mails you; the app meanwhile keeps showing the last good copy.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTS = ["bd_national_news.json", "eng_national_news.json", "online_news.json",
         "international_news.json", "bd_media_news.json", "bd_local_news.json"]
errors = []


def load(name):
    try:
        return json.loads((ROOT / name).read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{name}: file missing")
    except json.JSONDecodeError as e:
        errors.append(f"{name}: broken JSON at line {e.lineno} col {e.colno} — {e.msg}")
    return None


def need_url(where, v):
    if not isinstance(v, str) or not v.startswith(("http://", "https://")):
        errors.append(f"{where}: link must start with https:// (got {v!r})")


for name in LISTS:
    data = load(name)
    if data is None:
        continue
    if not isinstance(data, list):
        errors.append(f"{name}: must be a list [ ... ]"); continue
    seen = {}
    for i, e in enumerate(data, 1):
        where = f"{name} item {i}"
        if not isinstance(e, dict):
            errors.append(f"{where}: must be {{ ... }}"); continue
        if not str(e.get("title", "")).strip():
            errors.append(f"{where}: \"title\" is empty")
        need_url(where, e.get("pdfUrl"))
        u = str(e.get("pdfUrl", "")).rstrip("/").replace("://www.", "://")
        if u in seen:
            errors.append(f"{where}: same link as item {seen[u]} ({e.get('pdfUrl')})")
        seen[u] = i

cats = load("news_category.json")
if isinstance(cats, list):
    for i, c in enumerate(cats, 1):
        need_url(f"news_category.json item {i}", c.get("serverUrl"))
        if not c.get("cat_title"):
            errors.append(f"news_category.json item {i}: \"cat_title\" is empty")

tops = load("top_outlets.json")
if isinstance(tops, list):
    for i, t in enumerate(tops, 1):
        if not t.get("name"):
            errors.append(f"top_outlets.json item {i}: \"name\" is empty")
        need_url(f"top_outlets.json item {i}", t.get("url"))

for name in ["district_news.json", "app_version.json"]:
    load(name)

if errors:
    print("Problems found:\n  " + "\n  ".join(errors))
    sys.exit(1)
print("All lists OK")
