import yaml
from pathlib import Path

VALID_TOPICS = {"ai-dev", "design", "agile", "scrum", "xp", "team", "worklife"}

def test_sources_yaml_schema():
    data = yaml.safe_load(Path("sources.yaml").read_text(encoding="utf-8"))
    sources = data["sources"]
    assert len(sources) >= 10
    urls = set()
    for src in sources:
        assert set(src.keys()) == {"name", "feed", "lang", "topics"}
        assert src["feed"].startswith("https://")
        assert src["lang"] in ("ja", "en")
        assert src["topics"] and set(src["topics"]) <= VALID_TOPICS
        assert src["feed"] not in urls, f"duplicate feed: {src['feed']}"
        urls.add(src["feed"])
