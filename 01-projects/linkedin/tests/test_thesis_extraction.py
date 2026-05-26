from linter.thesis import ExtractionResult, extract_thesis


def test_extracts_single_tagged_thesis():
    body = (
        "Opening paragraph here.\n\n"
        "<THESIS>Strategy is problem-shaped, not goal-shaped.</THESIS>\n\n"
        "Closing remark."
    )
    result = extract_thesis(body)
    assert result.thesis == "Strategy is problem-shaped, not goal-shaped."
    assert result.warning is None
    # Tag stripped from clean_body but the sentence remains inline.
    assert "<THESIS>" not in result.clean_body
    assert "Strategy is problem-shaped" in result.clean_body


def test_no_tag_falls_back_to_first_sentence():
    body = "First sentence here. Second sentence here. Third."
    result = extract_thesis(body)
    assert result.thesis == "First sentence here."
    assert result.warning is not None
    assert "no thesis" in result.warning.lower()


def test_multiple_tags_uses_first_and_warns():
    body = (
        "<THESIS>First tagged thesis.</THESIS>\n\n"
        "Some body.\n\n"
        "<THESIS>Second tagged thesis.</THESIS>"
    )
    result = extract_thesis(body)
    assert result.thesis == "First tagged thesis."
    assert result.warning is not None
    assert "multiple" in result.warning.lower()
    # Both tag-pairs stripped from clean_body
    assert "<THESIS>" not in result.clean_body
    assert "First tagged thesis." in result.clean_body
    assert "Second tagged thesis." in result.clean_body


def test_empty_tag_falls_back():
    body = "Real first sentence. <THESIS></THESIS> Body text."
    result = extract_thesis(body)
    assert result.thesis == "Real first sentence."
    assert result.warning is not None
