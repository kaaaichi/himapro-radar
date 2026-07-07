#!/usr/bin/env python3
"""判定LLMの生出力ファイルを読み、data/YYYY-MM-DD.json と state/seen.json を更新する。
   信頼できない入力はファイル経由でのみ受け取り、json.loads以外では絶対に解釈しない
   (シェルやPythonのソース文字列に組み立てて実行することは絶対にしない)。"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.merge_judgment import parse_and_validate, build_data_record


def update_seen(seen_path, candidate_urls, today):
    seen = json.loads(Path(seen_path).read_text(encoding="utf-8")) if Path(seen_path).exists() else {}
    for url in candidate_urls:
        seen[url] = today
    Path(seen_path).write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")
    return seen


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--today", required=True)
    parser.add_argument("--judgment-input", required=True)
    parser.add_argument("--judge-output", required=True)
    parser.add_argument("--seen", required=True)
    parser.add_argument("--data-out", required=True)
    args = parser.parse_args(argv)

    judgment_input = json.loads(Path(args.judgment_input).read_text(encoding="utf-8"))
    judge_raw = Path(args.judge_output).read_text(encoding="utf-8")
    known_urls = {c["url"] for c in judgment_input["candidates"]}

    judged = parse_and_validate(judge_raw, known_urls)
    record = build_data_record(
        date=args.today,
        candidates=judgment_input["candidates"],
        judged=judged,
        capped_count=judgment_input["capped_count"],
        failures=judgment_input["failures"],
    )
    Path(args.data_out).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    update_seen(args.seen, [c["url"] for c in judgment_input["candidates"]], args.today)

    counts = {"S": 0, "A": 0, "B": 0}
    for item in record["items"]:
        counts[item["neta"]] += 1
    print(f"S:{counts['S']} A:{counts['A']} B:{counts['B']} rejected:{record['rejected_count']}")


if __name__ == "__main__":
    main(sys.argv[1:])
