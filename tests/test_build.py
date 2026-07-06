from scripts.build import render_day, render_index

DAY = {
    "date": "2026-07-06",
    "items": [
        {"url": "https://ex.com/s", "title": "S記事 <b>", "source": "Zenn(スクラム)", "lang": "ja",
         "summary": "要約です。", "topics": ["scrum"], "neta": "S", "hook": "逆転型で入るなら「◯◯」"},
        {"url": "https://ex.com/b", "title": "B記事", "source": "InfoQ", "lang": "en",
         "summary": "英語記事の日本語要約。", "topics": ["agile", "design"], "neta": "B"},
    ],
    "rejected_count": 5,
    "capped_count": 0,
    "failures": [{"name": "Qiita(アジャイル)", "error": "timeout"}],
}

def test_render_day_contains_sections_and_items():
    html = render_day(DAY)
    assert "2026-07-06" in html
    assert "今日のS判定" in html
    assert "S記事 &lt;b&gt;" in html            # エスケープされる
    assert "フック候補: 逆転型で入るなら「◯◯」" in html
    assert "スクラム" in html and "アジャイル" in html  # トピックは日本語ラベル表示
    assert "店長宛メモ" in html
    assert "Qiita(アジャイル): timeout" in html

def test_render_day_empty_items_reports_alive():
    html = render_day({"date": "2026-07-07", "items": [], "rejected_count": 0,
                       "capped_count": 0, "failures": []})
    assert "本日の新着なし(ループは正常稼働)" in html

def test_render_index_has_archive_links():
    latest = render_day(DAY)
    html = render_index(["2026-07-06", "2026-07-05"], latest)
    assert 'href="daily/2026-07-05.html"' in html
    assert 'href="daily/2026-07-06.html"' in html
    assert "アーカイブ" in html
