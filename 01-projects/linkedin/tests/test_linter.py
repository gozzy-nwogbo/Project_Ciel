from linter.linter import Annotation, Linter, Severity


def _lint(text: str) -> list[Annotation]:
    return Linter().lint(text, target_word_range=(80, 200))


def test_em_dash_hard_fails():
    annotations = _lint("This is a sentence — with an em-dash. " * 10)
    fails = [a for a in annotations if a.severity is Severity.HARD_FAIL]
    assert any(a.rule == "em_dash" for a in fails)


def test_contrastive_framing_hard_fails():
    text = "Not just an idea, an idea+. " + "Word " * 100
    fails = [a for a in _lint(text) if a.severity is Severity.HARD_FAIL]
    assert any(a.rule == "contrastive_framing" for a in fails)


def test_word_count_extreme_hard_fail():
    fails = [a for a in _lint("too short") if a.severity is Severity.HARD_FAIL]
    assert any(a.rule == "word_count_extreme" for a in fails)


def test_word_count_outside_target_soft_warn():
    text = "Word " * 250
    warns = [a for a in _lint(text) if a.severity is Severity.SOFT_WARN]
    assert any(a.rule == "word_count_target" for a in warns)


def test_clean_text_no_hard_fails():
    text = (
        "Built a small engine this week that picks two atoms from my second brain "
        "and asks where they overlap. Surfaced a tie between feedback loops in "
        "auth design and feedback loops in pedagogy. Same gear, different machines. "
        "Wondering what other domains the same gear runs in. "
    ) * 2
    fails = [a for a in _lint(text) if a.severity is Severity.HARD_FAIL]
    assert fails == []
