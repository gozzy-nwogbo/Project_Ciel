"""Tests for the generalized <TAG>...</TAG> extractor."""
from linter.tagged import extract_tagged


def test_extract_tagged_finds_single_tag():
    body = "Intro. <THESIS>This is the thesis.</THESIS> Outro."
    result = extract_tagged(body, "THESIS")
    assert result.extracted == "This is the thesis."
    assert result.clean_body == "Intro. This is the thesis. Outro."
    assert result.warning is None


def test_extract_tagged_falls_back_to_first_sentence_when_missing():
    body = "First sentence. Second sentence."
    result = extract_tagged(body, "CLAIM")
    assert result.extracted == "First sentence."
    assert result.warning == "no CLAIM tag found, used first sentence fallback"


def test_extract_tagged_warns_on_multiple_tags():
    body = "<CLAIM>first claim</CLAIM> middle <CLAIM>second claim</CLAIM>"
    result = extract_tagged(body, "CLAIM")
    assert result.extracted == "first claim"
    assert "multiple" in (result.warning or "")
    assert "<CLAIM>" not in result.clean_body
    assert "</CLAIM>" not in result.clean_body


def test_extract_tagged_treats_empty_tag_as_missing():
    body = "Intro. <CLAIM></CLAIM> Outro."
    result = extract_tagged(body, "CLAIM")
    assert result.extracted == "Intro."
    assert "no CLAIM tag" in (result.warning or "")
