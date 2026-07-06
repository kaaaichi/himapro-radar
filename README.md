# himapro radar

公開ページ: https://kaaaichi.github.io/himapro-radar/

ひまプロ Podcast の元ネタ発掘のための日次リサーチループ。
毎朝 7:00 JST に Claude Code routine が起動し、固定ソース(sources.yaml)の新着を収集・採点して GitHub Pages に公開する。

## 🛑 停止手順(まずこれ)

1. Claude Code で `/schedule` を開き、routine **himapro-radar-daily** を無効化(disable)する
2. 完全にやめる場合は同 routine を削除する
3. これ以外に動いているものはない(webhook・Actionsなし)

## 仕組み

sources.yaml(固定リスト) → scripts/collect.py(巡回・既読差分) → Claude が選別・要約・ネタ度採点(.claude/skills/daily-radar) → data/YYYY-MM-DD.json → scripts/build.py → docs/(GitHub Pages)

- 既読管理: state/seen.json(外部メモリ)
- ソースの追加・削除は sources.yaml の編集のみ
- ネタ度: S=エピソード化候補 / A=ストック / B=参考

## ガードレール

- routine は日次1回・1本のみ。テスト用の高頻度 routine は作らない
- 書き込み先はこのリポジトリのみ
- 新着50件超の日は上位30件のみ判定し、残りは件数を「店長宛メモ」に記録
- 運用開始3日後に棚卸し(実行ログ・コスト・品質)

## ローカル実行(手動で1周)

```bash
source .venv/bin/activate
python3 scripts/collect.py      # state/inbox.json を生成
# → Claude Code で $daily-radar を実行(判定と data/*.json 生成)
python3 scripts/build.py        # docs/ を再生成
open docs/index.html
```
