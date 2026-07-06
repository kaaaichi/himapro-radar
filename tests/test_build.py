import json

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

def test_render_day_sorts_by_neta_and_sections():
    day = {
        "date": "2026-07-06",
        "items": [
            {"url": "https://ex.com/b", "title": "B記事", "source": "InfoQ", "lang": "en",
             "summary": "b", "topics": ["agile"], "neta": "B"},
            {"url": "https://ex.com/a", "title": "A記事", "source": "Zenn(アジャイル)", "lang": "ja",
             "summary": "a", "topics": ["agile"], "neta": "A", "hook": "h"},
            {"url": "https://ex.com/s", "title": "S記事", "source": "Ryuzee.com", "lang": "ja",
             "summary": "s", "topics": ["scrum"], "neta": "S", "hook": "h"},
        ],
        "rejected_count": 0, "capped_count": 0, "failures": [],
    }
    html = render_day(day)
    s_section = html.split("今日のS判定")[1].split("その他の新着")[0]
    rest_section = html.split("その他の新着")[1].split("店長宛メモ")[0]
    assert "S記事" in s_section and "S記事" not in rest_section
    assert "A記事" in rest_section and "B記事" in rest_section
    assert rest_section.index("A記事") < rest_section.index("B記事")


def test_render_index_rewrites_relative_links():
    latest = render_day(DAY)
    html = render_index(["2026-07-06"], latest)
    assert 'href="style.css"' in html
    assert 'href="index.html"' in html
    assert 'href="../' not in html


def test_main_skips_broken_json(tmp_path, monkeypatch, capsys):
    import scripts.build as build
    data = tmp_path / "data"
    docs = tmp_path / "docs"
    data.mkdir()
    (data / "2026-07-06.json").write_text(json.dumps(DAY), encoding="utf-8")
    (data / "2026-07-05.json").write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(build, "DATA_DIR", data)
    monkeypatch.setattr(build, "DOCS_DIR", docs)
    build.main()
    assert (docs / "daily" / "2026-07-06.html").exists()
    assert not (docs / "daily" / "2026-07-05.html").exists()
    assert (docs / "index.html").exists()
    assert "skip 2026-07-05" in capsys.readouterr().out


def test_render_item_blocks_dangerous_uri_schemes():
    day = dict(DAY)
    day["items"] = [{"url": "javascript:alert(1)", "title": "危険", "source": "X", "lang": "ja",
                     "summary": "s", "topics": ["design"], "neta": "B"}]
    html = render_day(day)
    assert "javascript:" not in html
