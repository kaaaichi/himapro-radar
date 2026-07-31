# himapro radar

公開ページ: https://kaaaichi.github.io/himapro-radar/

ひまプロ Podcast の元ネタ発掘のための日次リサーチループ。
毎朝 7:00 JST に Claude Code routine が起動し、固定ソース(sources.yaml)の新着を収集・採点して GitHub Pages に公開する。

## 🛑 停止手順(まずこれ)

**動いている実行基盤は2つある。止めるときは両方を確認すること。**

1. ローカル launchd(現在の実運用。実際に日次コミットを作っているのはこちら)

   ```bash
   launchctl unload ~/Library/LaunchAgents/com.himapro.radar.daily.plist
   ```

2. クラウド routine **himapro-radar-daily**(`trig_01254gPqxsP6d4EoTqaa1Juv`)を Claude Code の `/schedule` から無効化(disable)する。有効なら空振りでも課金される
3. これ以外に動いているものはない(webhook なし。GitHub Actions は gitleaks のみで日次実行には無関係)

## 仕組み

sources.yaml(固定リスト) → scripts/collect.py(巡回・既読差分) → Claude が選別・要約・ネタ度採点(.claude/skills/daily-radar) → data/YYYY-MM-DD.json → scripts/build.py → docs/(GitHub Pages)

- 既読管理: state/seen.json(外部メモリ)
- ソースの追加・削除は sources.yaml の編集のみ
- ネタ度: S=エピソード化候補 / A=ストック / B=参考

## 実行基盤

**2026-07-31 現在、クラウド routine への復帰作業中。** 検証が済むまでローカル launchd を残す(下記「移行状況」)。

### クラウド routine `himapro-radar-daily`(本命)

毎日 07:05 JST 起動。SKILL.md の手順に従い、クラウド環境が判定から push まで行う。Mac の電源・スリープ状態に依存しないのが利点。

2026-07-07 の初回検証では (a) egress 遮断で全15フィード403 (b) push 権限不足 の2点で失敗し、一度は不採用とした。**この2点は 2026-07-31 の再検証でいずれも解消済みを確認**(15フィード中14件が HTTP 200、`git push origin HEAD:main` 成功)。

不採用期間中に routine が再有効化されていたが、別の原因(下記)で 07/24〜07/31 は空振りしていた。

**既知の制約**: クラウド環境の egress プロキシは `tidyfirst.substack.com`(Kent Beck / Tidy First)のみ 403 で遮断する。当該フィードは `failures` に記録され、レーダーには載らない。ローカル launchd 実行では取得できるため、実行基盤による差分になる。

**注意(SKILL.md を編集するとき)**: クラウド環境のチェックアウトは **detached HEAD**。`git pull --rebase` と引数なしの `git push` はどちらも `You are not currently on a branch.` で失敗する。必ず `git checkout -B main origin/main` でブランチに乗せ、push は `git push origin HEAD:main` と明示すること。ガードレールが手順外コマンドを禁じているため、エージェントは自力でこの回避ができない。

### ローカル launchd(現在のフォールバック)

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

### 移行状況(2026-07-31 時点)

クラウド routine の不具合を修正したが、**クラウドが実際にコミットを push できたことはまだ未確認**。そのため launchd は意図的に稼働継続中。

二重実行にはならない。`run_daily.sh` は `origin/main` の履歴に当日の `radar:` コミットがあるかで判定するため、クラウドが 07:05 に push すれば 07:12 の launchd は `already completed today` でスキップする。この仕組みがそのまま検証装置になる。

- [ ] クラウド routine が日次コミットを push できたことを確認する(確認できたら launchd を `launchctl unload` して本項を更新)

## ガードレール

- routine は日次1回・1本のみ。テスト用の高頻度 routine は作らない
- 書き込み先はこのリポジトリのみ
- 新着50件超の日は上位30件のみ判定し、残りは件数を「店長宛メモ」に記録
- 運用開始3日後に棚卸し(実行ログ・コスト・品質)

## 棚卸し記録

- 運用開始: 2026-07-07(routine `himapro-radar-daily` 登録日)
- [ ] 2026-07-10 の棚卸し(実行ログ・コスト・レポート品質・S判定の妥当性)— 済んだら日付を書く
- 2026-07-31: クラウド routine の不調を調査。経緯 — 07/07 に egress・push 権限の問題で無効化 → 07/14 に launchd ラッパーで代替 → **07/24 に routine が再有効化されており、以降 07/31 まで毎日空振りしながら課金だけ発生していた**。原因は egress でも権限でもなく、クラウド環境が detached HEAD のため SKILL.md 手順0・手順7 の git コマンドが失敗していたこと。SKILL.md を修正済み

## ローカル実行(手動で1周)

```bash
source .venv/bin/activate
python3 scripts/collect.py      # state/inbox.json を生成
# → Claude Code で $daily-radar を実行(判定と data/*.json 生成)
python3 scripts/build.py        # docs/ を再生成
open docs/index.html
```
