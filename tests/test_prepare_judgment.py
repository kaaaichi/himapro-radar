from scripts.prepare_judgment import score_relevance, select_for_judgment

TOPIC_KEYWORDS = {
    "ai-dev": ["ai", "エージェント", "agent", "claude", "llm", "駆動開発", "coding agent"],
    "design": ["設計", "design", "architecture", "アーキテクチャ"],
    "agile": ["アジャイル", "agile"],
    "scrum": ["スクラム", "scrum", "スプリント"],
    "xp": ["xp", "エクストリームプログラミング", "tdd", "テスト駆動"],
    "team": ["チーム", "team", "組織", "マネジメント"],
    "worklife": ["仕事術", "働き方", "キャリア"],
}

def test_score_relevance_counts_keyword_hits():
    assert score_relevance("スクラムのふりかえりをAIエージェントに応用", TOPIC_KEYWORDS) >= 2
    assert score_relevance("週末の天気予報について", TOPIC_KEYWORDS) == 0

def test_select_for_judgment_caps_at_limit_by_score():
    items = [
        {"url": f"https://x/{i}", "title": t, "source": "s", "lang": "ja", "published": "2026-07-07"}
        for i, t in enumerate([
            "スクラムの話", "アジャイル開発について", "今日のランチ", "AIエージェント駆動開発",
        ])
    ]
    selected, capped = select_for_judgment(items, TOPIC_KEYWORDS, limit=2)
    assert len(selected) == 2
    assert capped == 2
    selected_titles = {s["title"] for s in selected}
    assert "今日のランチ" not in selected_titles

def test_select_for_judgment_under_limit_returns_all_no_cap():
    items = [{"url": "https://x/1", "title": "スクラムの話", "source": "s", "lang": "ja", "published": "2026-07-07"}]
    selected, capped = select_for_judgment(items, TOPIC_KEYWORDS, limit=40)
    assert len(selected) == 1
    assert capped == 0
