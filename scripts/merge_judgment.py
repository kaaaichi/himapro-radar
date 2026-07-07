#!/usr/bin/env python3
"""判定LLMの出力(信頼できない)を既知URL集合と厳密なスキーマで検証し、
   カノニカルな収集データ(url/title/source/lang)と突き合わせて data レコードを組み立てる。
   date と failures は常にスクリプト側の値を使い、LLM出力からは絶対に取らない。"""
import json

VALID_TOPICS = {"ai-dev", "design", "agile", "scrum", "xp", "team", "worklife"}
VALID_NETA = {"S", "A", "B"}


def parse_and_validate(raw_text, known_urls):
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"judge output is not valid JSON: {exc}")
    if not isinstance(parsed, list):
        raise ValueError("judge output must be a JSON array")

    judged = {}
    for entry in parsed:
        if not isinstance(entry, dict):
            continue
        url = entry.get("url")
        if url not in known_urls:
            continue
        if not entry.get("keep"):
            continue
        neta = entry.get("neta")
        if neta not in VALID_NETA:
            continue
        topics = entry.get("topics")
        if not topics or not isinstance(topics, list) or not set(topics) <= VALID_TOPICS:
            continue
        summary = entry.get("summary")
        if not summary or not isinstance(summary, str):
            continue
        hook = entry.get("hook")
        if neta in ("S", "A") and not hook:
            continue
        judged[url] = {"summary": summary, "topics": topics, "neta": neta, "hook": hook}
    return judged


def build_data_record(date, candidates, judged, capped_count, failures):
    items = []
    for c in candidates:
        j = judged.get(c["url"])
        if not j:
            continue
        items.append({
            "url": c["url"],
            "title": c["title"],
            "source": c["source"],
            "lang": c["lang"],
            "summary": j["summary"],
            "topics": j["topics"],
            "neta": j["neta"],
            **({"hook": j["hook"]} if j.get("hook") else {}),
        })
    rejected_count = len(candidates) - len(items)
    return {
        "date": date,
        "items": items,
        "rejected_count": rejected_count,
        "capped_count": capped_count,
        "failures": failures,
    }
