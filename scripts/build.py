#!/usr/bin/env python3
"""data/*.json から docs/ の静的HTMLを再生成する(決定的)。LLMは使わない。"""
import html as html_mod
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"gho_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9\-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def contains_secret(text):
    return any(p.search(text) for p in SECRET_PATTERNS)

TOPIC_LABELS = {
    "ai-dev": "AI駆動開発",
    "design": "設計",
    "agile": "アジャイル",
    "scrum": "スクラム",
    "xp": "XP",
    "team": "チーム開発",
    "worklife": "仕事術",
}
NETA_ORDER = {"S": 0, "A": 1, "B": 2}


def esc(s):
    return html_mod.escape(s or "", quote=True)


def render_item(it):
    url = it.get("url", "")
    if not url.startswith(("http://", "https://")):
        url = ""
    topics = "".join(
        f'<span class="topic">{esc(TOPIC_LABELS.get(t, t))}</span>'
        for t in it.get("topics", [])
    )
    hook = ""
    if it.get("hook"):
        hook = f'<p class="hook">フック候補: {esc(it["hook"])}</p>'
    return f'''<article class="item neta-{esc(it.get("neta", "B"))}">
  <div class="item-head"><span class="neta">{esc(it.get("neta", "B"))}</span>{topics}<span class="src">{esc(it.get("source", ""))}</span></div>
  <h3><a href="{esc(url)}">{esc(it.get("title", ""))}</a></h3>
  <p class="summary">{esc(it.get("summary", ""))}</p>
  {hook}
</article>'''


def render_day(day):
    items = sorted(day.get("items", []), key=lambda i: NETA_ORDER.get(i.get("neta"), 9))
    s_items = [i for i in items if i.get("neta") == "S"]
    rest = [i for i in items if i.get("neta") != "S"]

    memo_lines = [f'{esc(f["name"])}: {esc(f["error"])}' for f in day.get("failures", [])]
    if day.get("capped_count"):
        memo_lines.append(f'新着が多すぎたため {esc(str(day["capped_count"]))} 件を未判定でスキップ(翌日再登場)')
    if day.get("rejected_count"):
        memo_lines.append(f'トピック対象外として {esc(str(day["rejected_count"]))} 件をボツ')
    if not items:
        memo_lines.append("本日の新着なし(ループは正常稼働)")
    memo = "".join(f"<li>{line}</li>" for line in memo_lines) or "<li>特になし</li>"

    s_html = "".join(render_item(i) for i in s_items) or '<p class="empty">本日のS判定はありません</p>'
    rest_html = "".join(render_item(i) for i in rest) or '<p class="empty">なし</p>'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(day["date"])} | himapro radar</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header><a class="brand" href="../index.html">himapro radar</a><h1>{esc(day["date"])}</h1></header>
<main>
<section><h2>今日のS判定</h2>{s_html}</section>
<section><h2>その他の新着</h2>{rest_html}</section>
<section class="memo"><h2>店長宛メモ</h2><ul>{memo}</ul></section>
</main>
<footer>ひまじんプログラマーの週末エンジニアリングレッスン ── 元ネタ発掘レーダー</footer>
</body>
</html>'''


def render_index(days, latest_html):
    archive = "".join(f'<li><a href="daily/{esc(d)}.html">{esc(d)}</a></li>' for d in days)
    body = latest_html.replace('href="../', 'href="')
    return body.replace(
        "</main>",
        f'<section class="archive-sec"><h2>アーカイブ</h2><ul class="archive">{archive}</ul></section></main>',
    )


def main():
    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "daily").mkdir(exist_ok=True)
    days = sorted((p.stem for p in DATA_DIR.glob("*.json")), reverse=True)
    built = []
    latest_html = ""
    for d in days:
        try:
            raw = (DATA_DIR / f"{d}.json").read_text(encoding="utf-8")
            if contains_secret(raw):
                raise RuntimeError("secret-like string detected in data; refusing to publish")
            day = json.loads(raw)
            page = render_day(day)
        except Exception as exc:  # 壊れた日次ファイル・シークレット混入はスキップし、他の日のビルドは続行する
            print(f"skip {d}: {exc}")
            continue
        (DOCS_DIR / "daily" / f"{d}.html").write_text(page, encoding="utf-8")
        built.append(d)
        if not latest_html:
            latest_html = page
    if built:
        (DOCS_DIR / "index.html").write_text(render_index(built, latest_html), encoding="utf-8")
    print(f"built {len(built)} day(s)")


if __name__ == "__main__":
    main()
