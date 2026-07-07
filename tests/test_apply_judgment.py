import json
import os
import pytest
from scripts.apply_judgment import update_seen, main

def test_update_seen_adds_all_candidate_urls(tmp_path):
    seen_path = tmp_path / "seen.json"
    seen_path.write_text(json.dumps({"https://old": "2026-07-01"}), encoding="utf-8")
    update_seen(str(seen_path), ["https://a", "https://b"], "2026-07-07")
    seen = json.loads(seen_path.read_text())
    assert seen == {"https://old": "2026-07-01", "https://a": "2026-07-07", "https://b": "2026-07-07"}

def test_main_end_to_end_with_files(tmp_path, capsys):
    judgment_input = {
        "date": "2026-07-07",
        "candidates": [
            {"url": "https://a", "title": "Aタイトル", "source": "SrcA", "lang": "ja", "published": "2026-07-07"},
        ],
        "capped_count": 0,
        "failures": [],
    }
    (tmp_path / "judgment_input.json").write_text(json.dumps(judgment_input), encoding="utf-8")
    (tmp_path / "judge_output.txt").write_text(json.dumps([
        {"url": "https://a", "keep": True, "summary": "要約", "topics": ["scrum"], "neta": "S", "hook": "h"}
    ]), encoding="utf-8")
    (tmp_path / "seen.json").write_text("{}", encoding="utf-8")
    data_out = tmp_path / "data_2026-07-07.json"

    main([
        "--today", "2026-07-07",
        "--judgment-input", str(tmp_path / "judgment_input.json"),
        "--judge-output", str(tmp_path / "judge_output.txt"),
        "--seen", str(tmp_path / "seen.json"),
        "--data-out", str(data_out),
    ])

    record = json.loads(data_out.read_text())
    assert record["items"][0]["url"] == "https://a"
    assert record["items"][0]["title"] == "Aタイトル"
    seen = json.loads((tmp_path / "seen.json").read_text())
    assert seen["https://a"] == "2026-07-07"
    assert "S:1 A:0 B:0 rejected:0" in capsys.readouterr().out

def test_main_handles_malicious_judge_output_safely(tmp_path):
    # 生出力に「コード注入」を模した文字列が入っていても、ファイル経由でJSONとしてのみ扱われ実行されないことを確認
    judgment_input = {
        "date": "2026-07-07",
        "candidates": [{"url": "https://a", "title": "A", "source": "S", "lang": "ja", "published": "2026-07-07"}],
        "capped_count": 0,
        "failures": [],
    }
    (tmp_path / "judgment_input.json").write_text(json.dumps(judgment_input), encoding="utf-8")
    (tmp_path / "judge_output.txt").write_text('"""; import os; os.system("touch /tmp/pwned_test_marker") #', encoding="utf-8")
    (tmp_path / "seen.json").write_text("{}", encoding="utf-8")
    data_out = tmp_path / "out.json"

    with pytest.raises(ValueError):
        main([
            "--today", "2026-07-07",
            "--judgment-input", str(tmp_path / "judgment_input.json"),
            "--judge-output", str(tmp_path / "judge_output.txt"),
            "--seen", str(tmp_path / "seen.json"),
            "--data-out", str(data_out),
        ])
    assert not os.path.exists("/tmp/pwned_test_marker")
