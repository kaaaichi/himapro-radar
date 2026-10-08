# himapro-radar (正本: /Users/iidakaichiro/develop/himapro-radar-codex)

- 日次実行の手順は `.claude/skills/daily-radar/SKILL.md` に従う。排他ロックは `.git/claude-radar.lock`。
- **コミットに Co-Authored-By などの Claude 名義 trailer を付けない**(radar の日次コミット・保守コミットとも)。
- `git checkout -B` / `git reset --hard` / force push は使わない。更新は `git merge --ff-only origin/main` のみ。
- `scripts/run_daily.sh` は旧コピー `~/develop/himapro-radar` 用の旧 launchd 版(REPO_DIR が旧コピー、trailer 付き、引数なし push)。非推奨・不使用。
- `.git/codex-radar.lock` は旧 Codex 自動化のロック。Claude の実行では触らない。
