"""Voice linter for LinkedIn post drafts."""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml


class Severity(str, Enum):
    HARD_FAIL = "hard_fail"
    SOFT_WARN = "soft_warn"


@dataclass
class Annotation:
    rule: str
    severity: Severity
    message: str
    match: str = ""


_PASSIVE_VERBS = re.compile(
    r"\b(am|is|are|was|were|be|been|being)\s+\w+ed\b",
    flags=re.IGNORECASE,
)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _passive_ratio(text: str) -> float:
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return 0.0
    passive = sum(1 for s in sentences if _PASSIVE_VERBS.search(s))
    return passive / len(sentences)


class Linter:
    def __init__(self, rules_path: Path | None = None):
        if rules_path is None:
            rules_path = Path(__file__).parent / "rules.yml"
        self.rules = yaml.safe_load(Path(rules_path).read_text())

    def lint(self, text: str, target_word_range: tuple[int, int] = (80, 200)) -> list[Annotation]:
        out: list[Annotation] = []
        wc = _word_count(text)

        for rule_name, rule in (self.rules.get("hard_fail") or {}).items():
            ann = self._eval_rule(rule_name, rule, text, wc, Severity.HARD_FAIL, target_word_range)
            out.extend(ann)
        for rule_name, rule in (self.rules.get("soft_warn") or {}).items():
            ann = self._eval_rule(rule_name, rule, text, wc, Severity.SOFT_WARN, target_word_range)
            out.extend(ann)
        return out

    def _eval_rule(self, name, rule, text, wc, severity, target_range) -> list[Annotation]:
        out: list[Annotation] = []
        kind = rule.get("type", "regex")
        msg = rule.get("message", name)

        if kind == "regex" or (kind == "regex" and "pattern" in rule):
            pattern = rule.get("pattern")
            if pattern:
                for m in re.finditer(pattern, text):
                    out.append(Annotation(rule=name, severity=severity, message=msg, match=m.group(0)))
        elif "pattern" in rule:
            for m in re.finditer(rule["pattern"], text):
                out.append(Annotation(rule=name, severity=severity, message=msg, match=m.group(0)))
        elif kind == "ratio":
            per = rule["per_words"]
            max_count = rule["max"]
            allowed = max(1, wc // per) * max_count
            actual = text.count("!")
            if actual > allowed:
                out.append(Annotation(rule=name, severity=severity, message=f"{msg} ({actual} found, {allowed} allowed)"))
        elif kind == "word_count":
            if wc < rule["min"] or wc > rule["max"]:
                out.append(Annotation(rule=name, severity=severity, message=f"{msg} (got {wc})"))
        elif kind == "word_count_target":
            lo, hi = target_range
            if wc < lo or wc > hi:
                out.append(Annotation(rule=name, severity=severity, message=f"{msg} (got {wc}, target {lo}-{hi})"))
        elif kind == "passive_ratio":
            ratio = _passive_ratio(text)
            if ratio > rule["threshold"]:
                out.append(Annotation(rule=name, severity=severity, message=f"{msg} ({ratio:.0%})"))
        return out

    def has_hard_fail(self, annotations: list[Annotation]) -> bool:
        return any(a.severity is Severity.HARD_FAIL for a in annotations)
