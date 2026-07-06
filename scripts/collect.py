#!/usr/bin/env python3
"""sources.yaml のフィードを巡回し、既読(state/seen.json)との差分を state/inbox.json に書く。

決定的スクリプト。判断(要約・採点)は行わない。失敗したフィードはスキップして記録し、ループは止めない。
"""
import json
import socket
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "sources.yaml"
SEEN_PATH = ROOT / "state" / "seen.json"
INBOX_PATH = ROOT / "state" / "inbox.json"

JST = timezone(timedelta(hours=9))

socket.setdefaulttimeout(10)


def load_sources(path=SOURCES_PATH):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return data["sources"]


def load_seen(path=SEEN_PATH):
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def normalize_entry(entry, source):
    url = entry.get("link", "").strip()
    title = " ".join(entry.get("title", "").split())
    published = ""
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            published = time.strftime("%Y-%m-%d", tuple(t))
            break
    return {
        "url": url,
        "title": title,
        "source": source["name"],
        "lang": source["lang"],
        "published": published,
    }


def diff_new(items, seen):
    out = []
    picked = set()
    for it in items:
        url = it["url"]
        if not url.startswith(("http://", "https://")) or url in seen or url in picked:
            continue
        picked.add(url)
        out.append(it)
    return out


def main():
    sources = load_sources()
    seen = load_seen()
    items = []
    failures = []
    for src in sources:
        try:
            parsed = feedparser.parse(src["feed"])
            if parsed.bozo and not parsed.entries:
                raise RuntimeError(str(parsed.bozo_exception))
            for entry in parsed.entries:
                items.append(normalize_entry(entry, src))
        except Exception as exc:  # フィード単位で握りつぶし、記録してループは続行
            failures.append({"name": src["name"], "error": str(exc)[:200]})
    new_items = diff_new(items, seen)
    inbox = {
        "date": datetime.now(JST).strftime("%Y-%m-%d"),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_feeds": len(sources),
        "new_items": new_items,
        "failures": failures,
    }
    INBOX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INBOX_PATH.write_text(json.dumps(inbox, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"feeds={len(sources)} new={len(new_items)} failures={len(failures)}")


if __name__ == "__main__":
    main()
