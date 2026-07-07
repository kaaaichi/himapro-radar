import json
from scripts.merge_judgment import parse_and_validate, build_data_record

CANDIDATES = [
    {"url": "https://a", "title": "Aタイトル", "source": "SrcA", "lang": "ja", "published": "2026-07-07"},
    {"url": "https://b", "title": "Bタイトル", "source": "SrcB", "lang": "en", "published": "2026-07-07"},
]

def test_parse_and_validate_accepts_known_urls_only():
    raw = json.dumps([
        {"url": "https://a", "keep": True, "summary": "要約A", "topics": ["scrum"], "neta": "S", "hook": "h"},
        {"url": "https://evil-hallucinated", "keep": True, "summary": "x", "topics": ["scrum"], "neta": "S", "hook": "h"},
    ])
    known_urls = {c["url"] for c in CANDIDATES}
    judged = parse_and_validate(raw, known_urls)
    assert "https://a" in judged
    assert "https://evil-hallucinated" not in judged

def test_parse_and_validate_rejects_invalid_neta():
    raw = json.dumps([{"url": "https://a", "keep": True, "summary": "s", "topics": ["scrum"], "neta": "X", "hook": "h"}])
    judged = parse_and_validate(raw, {"https://a"})
    assert "https://a" not in judged

def test_parse_and_validate_rejects_s_without_hook():
    raw = json.dumps([{"url": "https://a", "keep": True, "summary": "s", "topics": ["scrum"], "neta": "S"}])
    judged = parse_and_validate(raw, {"https://a"})
    assert "https://a" not in judged

def test_parse_and_validate_raises_on_malformed_json():
    import pytest
    with pytest.raises(ValueError):
        parse_and_validate("not json{{{", {"https://a"})

def test_parse_and_validate_rejects_non_boolean_keep():
    raw = json.dumps([{"url": "https://a", "keep": "false", "summary": "s", "topics": ["scrum"], "neta": "S", "hook": "h"}])
    judged = parse_and_validate(raw, {"https://a"})
    assert "https://a" not in judged

def test_parse_and_validate_ignores_non_string_url():
    raw = json.dumps([{"url": ["https://a"], "keep": True, "summary": "s", "topics": ["scrum"], "neta": "S", "hook": "h"}])
    judged = parse_and_validate(raw, {"https://a"})
    assert judged == {}

def test_build_data_record_uses_canonical_fields_and_own_date_and_failures():
    judged = {"https://a": {"keep": True, "summary": "要約A", "topics": ["scrum"], "neta": "S", "hook": "h"}}
    record = build_data_record(
        date="2026-07-07",
        candidates=CANDIDATES,
        judged=judged,
        capped_count=3,
        failures=[{"name": "X", "error": "timeout"}],
    )
    assert record["date"] == "2026-07-07"
    assert record["capped_count"] == 3
    assert record["failures"] == [{"name": "X", "error": "timeout"}]
    items = record["items"]
    assert len(items) == 1
    assert items[0]["url"] == "https://a"
    assert items[0]["title"] == "Aタイトル"
    assert items[0]["source"] == "SrcA"
    assert record["rejected_count"] == 1
