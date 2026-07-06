---
name: daily-radar
description: ひまプロ Podcast 元ネタ発掘の日次レーダー。固定ソースの新着を収集し、選別・日本語要約・ネタ度採点して GitHub Pages を更新する。毎朝の routine から実行される。
---

# daily-radar 実行手順

あなたの役割は「編集者」。収集と描画はスクリプトがやる。あなたは選別・要約・採点だけを行う。

## 手順

1. **収集(決定的)**: `source .venv/bin/activate && python3 scripts/collect.py` を実行し、`state/inbox.json` を読む
2. **上限ガード**: new_items が50件を超える場合、番組トピックへの関連が高そうな上位30件だけを判定対象にする。スキップ件数を `capped_count` に記録する(スキップ分は seen に入れない=翌日再登場する)
3. **選別と判定**: 判定対象の各アイテムについて:
   - 番組トピック(AI駆動開発/設計/アジャイル/スクラム/XP/チーム開発/仕事術)のどれにも該当しなければボツ(`rejected_count` にカウントし、URLは seen に入れる)
   - 採用するものには以下を付ける:
     - `summary`: 日本語要約2〜3文。英語記事も必ず日本語で。タイトルだけで不明瞭な場合のみ WebFetch で本文確認(最大5件まで)
     - `topics`: 7 slug (`ai-dev` `design` `agile` `scrum` `xp` `team` `worklife`) から1〜2個
     - `neta`: S / A / B — S=エピソード化候補(意外性がある・番組の逆転型フックが作れる・初級〜中級に語れる、の2つ以上を満たす)/ A=ネタ帳ストック(1つ満たす)/ B=参考情報
     - `hook`: S と A のみ。フック候補を一言(例: 逆転型で入るなら「◯◯」)
4. **保存**: 以下のスキーマで `data/YYYY-MM-DD.json`(今日の日付)に書く:

   ```json
   {
     "date": "YYYY-MM-DD",
     "items": [{"url": "...", "title": "...", "source": "...", "lang": "ja",
                "summary": "...", "topics": ["scrum"], "neta": "S", "hook": "..."}],
     "rejected_count": 0,
     "capped_count": 0,
     "failures": []
   }
   ```

   `failures` は inbox.json の failures をそのまま転記する
5. **seen 更新**: 判定した全URL(採用+ボツ)を `state/seen.json` に `{url: "YYYY-MM-DD"}` 形式で追加する。スキップ(capped)分は入れない
6. **描画(決定的)**: `python3 scripts/build.py` を実行する
7. **コミット**: `git add data state/seen.json docs && git commit -m "radar: YYYY-MM-DD (S:n A:n B:n)" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" && git push`

## ガードレール(必ず守る)

- 書き込み先はこのリポジトリ(himapro-radar)のみ。他のリポジトリ・外部サービスに書き込まない
- HTMLを直接編集しない(必ず build.py 経由)
- sources.yaml をこの手順の中で書き換えない(ソース管理は人間の仕事)
- collect.py が全フィード失敗を報告しても、その事実を failures としてレポートに残し、正常にコミットして終了する(ループを止めない)
