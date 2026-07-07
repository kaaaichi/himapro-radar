#!/usr/bin/env python3
"""inbox.json の新着を関連度でスコアリングし、判定LLMに渡す上位N件を選ぶ(決定的、LLM不使用)。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX_PATH = ROOT / "state" / "inbox.json"
OUTPUT_PATH = ROOT / "state" / "judgment_input.json"
LIMIT = 40

TOPIC_KEYWORDS = {
    "ai-dev": ["ai", "エージェント", "agent", "claude", "llm", "駆動開発", "coding agent"],
    "design": ["設計", "design", "architecture", "アーキテクチャ"],
    "agile": ["アジャイル", "agile"],
    "scrum": ["スクラム", "scrum", "スプリント"],
    "xp": ["xp", "エクストリームプログラミング", "tdd", "テスト駆動"],
    "team": ["チーム", "team", "組織", "マネジメント"],
    "worklife": ["仕事術", "働き方", "キャリア"],
}


def score_relevance(title, keywords_map=TOPIC_KEYWORDS):
    t = title.lower()
    score = 0
    for kws in keywords_map.values():
        for kw in kws:
            if kw.lower() in t:
                score += 1
    return score


def select_for_judgment(items, keywords_map=TOPIC_KEYWORDS, limit=LIMIT):
    scored = sorted(items, key=lambda i: score_relevance(i["title"], keywords_map), reverse=True)
    selected = scored[:limit]
    capped = max(0, len(items) - limit)
    return selected, capped


def main():
    inbox = json.loads(INBOX_PATH.read_text(encoding="utf-8"))
    selected, capped = select_for_judgment(inbox["new_items"])
    output = {
        "date": inbox["date"],
        "candidates": selected,
        "capped_count": capped,
        "failures": inbox["failures"],
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"selected={len(selected)} capped={capped}")


if __name__ == "__main__":
    main()
