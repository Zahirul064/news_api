"""Write how many outlets each category has into news_category.json.

The app shows these numbers on the home dashboard. Keeping them here means the
app no longer downloads every category list on start-up just to count it.
Runs from .github/workflows/counts.yml whenever a *_news.json file changes.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAT = ROOT / "news_category.json"


def count_of(file_name: str) -> int | None:
    path = ROOT / file_name
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and "divisions" in data:  # district_news.json
        return sum(len(d.get("news", [])) for v in data["divisions"] for d in v.get("districts", []))
    return None


def main() -> int:
    cats = json.loads(CAT.read_text(encoding="utf-8"))
    changed = False
    for c in cats:
        name = c.get("serverUrl", "").rsplit("/", 1)[-1]
        n = count_of(name)
        if n is not None and c.get("count") != n:
            c["count"] = n
            changed = True
    if changed:
        CAT.write_text(json.dumps(cats, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print("updated" if changed else "no change", [(c["cat_title"], c.get("count")) for c in cats])
    return 0


if __name__ == "__main__":
    sys.exit(main())
