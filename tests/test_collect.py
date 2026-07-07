import io

from scripts.collect import normalize_entry, diff_new, read_limited, MAX_FEED_BYTES

SRC = {"name": "テストソース", "feed": "https://x", "lang": "ja", "topics": ["design"]}

def test_normalize_entry_basic():
    entry = {
        "link": " https://example.com/a ",
        "title": "改行\nあり  タイトル",
        "published_parsed": (2026, 7, 6, 0, 0, 0, 6, 187, 0),
    }
    it = normalize_entry(entry, SRC)
    assert it == {
        "url": "https://example.com/a",
        "title": "改行 あり タイトル",
        "source": "テストソース",
        "lang": "ja",
        "published": "2026-07-06",
    }

def test_normalize_entry_missing_fields():
    it = normalize_entry({}, SRC)
    assert it["url"] == ""
    assert it["title"] == ""
    assert it["published"] == ""

def test_diff_new_skips_seen_duplicates_and_empty_urls():
    items = [
        {"url": "https://a", "title": "既読"},
        {"url": "https://b", "title": "新規"},
        {"url": "https://b", "title": "同一URLの重複"},
        {"url": "", "title": "URLなし"},
        {"url": "javascript:alert(1)", "title": "危険URI"},
    ]
    out = diff_new(items, {"https://a": "2026-07-05"})
    assert [i["title"] for i in out] == ["新規"]

def test_read_limited_allows_under_cap():
    assert read_limited(io.BytesIO(b"hello"), limit=10) == b"hello"

def test_read_limited_rejects_over_cap():
    import pytest
    with pytest.raises(RuntimeError):
        read_limited(io.BytesIO(b"x" * 20), limit=10)
