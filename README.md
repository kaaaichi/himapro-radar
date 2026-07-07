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

## 実行基盤(ローカル launchd)

クラウドの Claude Code routine は `claude/` ブランチ制限と egress 制限のため、このプロジェクトの用途(main への直接 push、外部フィード取得)と相性が悪く不採用とした(検証記録: `.superpowers/sdd/progress.md`)。代わりに、このMacBookの launchd で日次実行する。

**セキュリティ設計**: 信頼できない記事本文を読む判定ステップ(`claude -p`)には `WebFetch` 以外のツールを一切与えない。Bash実行・ファイル書き込み・git操作はすべて `run_daily.sh`(決定的シェルスクリプト)側が行うため、記事内容にプロンプトインジェクションが仕込まれていても、判定LLMがコマンド実行やpushをすることはできない。判定LLMの生出力は必ずファイル経由(`state/judge_output.txt`)で `scripts/apply_judgment.py` に渡され、`json.loads` でデータとしてのみ解釈される(シェルやPythonのソースコードに組み立てることは一切しない)。既知URL集合・スキーマとの照合で不正な出力は破棄する(fail-closed)。

- 定義ファイル: `~/Library/LaunchAgents/com.himapro.radar.daily.plist`(このMac固有、git管理外)
- 実行スクリプト: `scripts/run_daily.sh`
- トリガー: 毎日7:00 + 30分ごとのポーリング。**Macがスリープ中は動かない** — その日最初にMacを開いた(起きた)タイミングの30分以内に、まだ未完了なら自動実行される(冪等性チェックにより1日1回のみ実際に実行)
- ログ: `logs/YYYY-MM-DD.log`(git管理外)

### 停止手順(このMac固有)

```bash
launchctl unload ~/Library/LaunchAgents/com.himapro.radar.daily.plist
```

再開:
```bash
launchctl load ~/Library/LaunchAgents/com.himapro.radar.daily.plist
```

## ガードレール

- routine は日次1回・1本のみ。テスト用の高頻度 routine は作らない
- 書き込み先はこのリポジトリのみ
- 新着50件超の日は上位30件のみ判定し、残りは件数を「店長宛メモ」に記録
- 運用開始3日後に棚卸し(実行ログ・コスト・品質)

## 棚卸し記録

- 運用開始: 2026-07-07(routine `himapro-radar-daily` 登録日)
- [ ] 2026-07-10 の棚卸し(実行ログ・コスト・レポート品質・S判定の妥当性)— 済んだら日付を書く

## ローカル実行(手動で1周)

```bash
source .venv/bin/activate
python3 scripts/collect.py      # state/inbox.json を生成
# → Claude Code で $daily-radar を実行(判定と data/*.json 生成)
python3 scripts/build.py        # docs/ を再生成
open docs/index.html
```
