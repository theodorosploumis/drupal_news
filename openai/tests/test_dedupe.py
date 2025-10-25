from utils.dedupe import dedupe_items


def test_dedupe_removes_duplicates():
    items = [
        {"title": "A", "url": "https://example.com/a", "guid": "1", "summary": "", "source": "s"},
        {"title": "B", "url": "https://example.com/a", "guid": "1", "summary": "", "source": "s"},
    ]
    result = dedupe_items(items)
    assert len(result) == 1
    assert result[0]["title"] == "A"
