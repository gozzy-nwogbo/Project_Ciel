# LinkedIn Engine v1.0 Implementation Plan — Part 2

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Prerequisite:** Part 1 (Phases A–F) must be complete. See `01-projects/linkedin/docs/2026-05-24-v1-0-implementation-plan.md`.

**Covers:** Phases G–M — strategies, linter, text generator, renderer, skill, CLI, integration tests.

---

## Phase G — Strategy implementations

### Task G1: `source_spotlight` strategy

**Files:**
- Create: `01-projects/linkedin/src/strategies/source_spotlight.py`
- Create: `01-projects/linkedin/tests/test_source_spotlight.py`
- Create: `01-projects/linkedin/tests/fixtures/atoms/concepts/third-concept.md` (additional fixture for richer tests)

- [ ] **Step 1: Add fixture atoms shared by multiple strategies**

Create `01-projects/linkedin/tests/fixtures/atoms/concepts/third-concept.md`:

```markdown
---
title: Third Concept
type: concept
source_date: 2026-05-03
tags: [storytelling, narrative]
domain: writing
origin: test-fixture
---

A storytelling-domain concept for cross-domain tests.
```

Create `01-projects/linkedin/tests/fixtures/atoms/connections/sample-to-third.md`:

```markdown
---
title: sample-to-third
type: connection
source_date: 2026-05-03
from: Sample Concept
to: Third Concept
connection_type: analogical
---

The mechanism in Sample Concept maps analogically to Third Concept's structure.
```

- [ ] **Step 2: Write failing test**

```python
# tests/test_source_spotlight.py
from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.source_spotlight import SourceSpotlight
from usage.atom_usage import AtomUsageTracker


def test_source_spotlight_returns_brief(atom_source, project_root):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json")
    ctx = StrategyContext(loader=loader, graph=graph, atom_tracker=tracker)

    strategy = SourceSpotlight()
    brief = strategy.generate_brief(ctx, {"source": "test-fixture", "atom_count": 2})

    assert brief.strategy == "source_spotlight"
    assert len(brief.atoms_used) >= 2
    assert "test-fixture" in brief.angle or brief.strategy_params["source"] == "test-fixture"
    assert all(ref.role == "primary" for ref in brief.atoms_used)


def test_source_spotlight_excludes_cooldown(atom_source, project_root):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json")
    tracker.mark_used("sample-concept", role="primary", post_id="prev")
    ctx = StrategyContext(loader=loader, graph=graph, atom_tracker=tracker)

    strategy = SourceSpotlight()
    brief = strategy.generate_brief(ctx, {"source": "test-fixture", "atom_count": 2})
    slugs = {ref.slug for ref in brief.atoms_used}
    assert "sample-concept" not in slugs
```

- [ ] **Step 3: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_source_spotlight.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 4: Implement `src/strategies/source_spotlight.py`**

```python
"""source_spotlight strategy — N atoms from one source + secondary domain finder."""
from __future__ import annotations

import random
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import StrategyContext, eligible_atoms


class SourceSpotlight:
    name = "source_spotlight"

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        source = params.get("source")
        if not source:
            raise ValueError("source_spotlight requires 'source' param")
        atom_count = int(params.get("atom_count", 3))

        candidates = [
            a for a in ctx.loader.load_by_source(source)
            if a.type != "connection"
        ]
        candidates = eligible_atoms(candidates, ctx.atom_tracker, role="primary")
        if len(candidates) < atom_count:
            raise ValueError(
                f"Not enough eligible atoms for source '{source}': "
                f"need {atom_count}, have {len(candidates)}"
            )

        candidates.sort(key=lambda a: a.source_date or "", reverse=True)
        picks = candidates[: atom_count * 2]
        random.shuffle(picks)
        chosen = picks[:atom_count]

        secondary_domain = self._find_secondary_domain(ctx, chosen)
        angle = self._compose_angle(source, secondary_domain, chosen)

        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=self._make_slug(now, source),
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={"source": source, "atom_count": atom_count, "secondary_domain": secondary_domain},
            atoms_used=[AtomRef(slug=a.slug, role="primary", source=source) for a in chosen],
            angle=angle,
            visual_tier="1_diagram",
            status=Status.DRAFTING,
            topic_tags=sorted({t for a in chosen for t in a.tags}),
        )

    def _find_secondary_domain(self, ctx: StrategyContext, chosen: list) -> Optional[str]:
        """Find a domain that ≥2 of the chosen atoms connect to (via their neighbors)."""
        neighbor_domains: Counter[str] = Counter()
        chosen_slugs = {a.slug for a in chosen}
        chosen_domains = {a.domain for a in chosen if a.domain}
        for atom in chosen:
            for neighbor_slug in ctx.graph.neighbors(atom.slug):
                if neighbor_slug in chosen_slugs:
                    continue
                neighbor = ctx.loader.load_one(neighbor_slug)
                if not neighbor or not neighbor.domain:
                    continue
                if neighbor.domain in chosen_domains:
                    continue
                neighbor_domains[neighbor.domain] += 1
        if not neighbor_domains:
            return None
        top, count = neighbor_domains.most_common(1)[0]
        return top if count >= 2 else None

    def _compose_angle(self, source: str, secondary: Optional[str], chosen: list) -> str:
        n = len(chosen)
        if secondary:
            return f"{n} ideas from {source} all touch {secondary}. Here's why that matters."
        joined = ", ".join(a.title for a in chosen)
        return f"{n} ideas from {source} — {joined} — sharing one pattern."

    def _make_slug(self, now: datetime, source: str) -> str:
        date = now.strftime("%Y-%m-%d")
        source_slug = source.lower().replace(" ", "-").replace(".", "")
        return f"{date}-{source_slug}-spotlight"
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_source_spotlight.py -v
```

Expected: PASS both tests.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/strategies/source_spotlight.py 01-projects/linkedin/tests/test_source_spotlight.py 01-projects/linkedin/tests/fixtures/atoms/
git commit -m "feat(linkedin): source_spotlight strategy with secondary-domain finder"
```

---

### Task G2: `two_atom_bridge` strategy

**Files:**
- Create: `01-projects/linkedin/src/strategies/two_atom_bridge.py`
- Create: `01-projects/linkedin/tests/test_two_atom_bridge.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_two_atom_bridge.py
import pytest

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.two_atom_bridge import TwoAtomBridge
from usage.atom_usage import AtomUsageTracker
from usage.connection_usage import ConnectionUsageTracker


def _ctx(atom_source, project_root):
    loader = AtomLoader(atom_source)
    return StrategyContext(
        loader=loader,
        graph=ConnectionGraph(loader.load_all()),
        atom_tracker=AtomUsageTracker(project_root / "state" / "atom-usage.json"),
        connection_tracker=ConnectionUsageTracker(project_root / "state" / "connection-usage.json"),
    )


def test_explicit_pair_uses_typed_claim(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = TwoAtomBridge()
    brief = strategy.generate_brief(ctx, {
        "atom_a": "sample-concept",
        "atom_b": "third-concept",
    })
    assert brief.strategy == "two_atom_bridge"
    assert len(brief.atoms_used) == 2
    assert brief.strategy_params.get("connection_type") == "analogical"


def test_same_domain_rejected(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = TwoAtomBridge()
    with pytest.raises(ValueError, match="same domain"):
        strategy.generate_brief(ctx, {
            "atom_a": "sample-concept",
            "atom_b": "another-concept",
        })
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_two_atom_bridge.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/strategies/two_atom_bridge.py`**

```python
"""two_atom_bridge — surface the shared mechanism across two atoms from different domains."""
from __future__ import annotations

import uuid

from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import StrategyContext


class TwoAtomBridge:
    name = "two_atom_bridge"

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        slug_a = params.get("atom_a")
        slug_b = params.get("atom_b")
        if not slug_a or not slug_b:
            raise ValueError("two_atom_bridge requires 'atom_a' and 'atom_b'")
        atom_a = ctx.loader.load_one(slug_a)
        atom_b = ctx.loader.load_one(slug_b)
        if not atom_a or not atom_b:
            raise ValueError(f"Unknown atom slug(s): {slug_a}, {slug_b}")
        if atom_a.domain and atom_b.domain and atom_a.domain == atom_b.domain:
            raise ValueError(
                f"Atoms share same domain '{atom_a.domain}' — bridge requires different domains"
            )

        connection_type = "general"
        claim = ""
        for edge in ctx.graph.edges_for(slug_a):
            if {edge.from_slug, edge.to_slug} == {slug_a, slug_b}:
                connection_type = edge.connection_type
                claim = edge.claim
                break

        if ctx.connection_tracker and ctx.connection_tracker.is_in_cooldown(slug_a, slug_b):
            raise ValueError(
                f"Connection {slug_a} <-> {slug_b} is in cooldown"
            )

        angle = self._compose_angle(atom_a, atom_b, connection_type)
        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=f"{now.strftime('%Y-%m-%d')}-bridge-{slug_a}-{slug_b}",
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={
                "atom_a": slug_a,
                "atom_b": slug_b,
                "connection_type": connection_type,
                "claim": claim,
            },
            atoms_used=[
                AtomRef(slug=slug_a, role="primary"),
                AtomRef(slug=slug_b, role="primary"),
            ],
            angle=angle,
            visual_tier="1_diagram",
            status=Status.DRAFTING,
            topic_tags=sorted(set(atom_a.tags + atom_b.tags)),
        )

    def _compose_angle(self, a, b, connection_type: str) -> str:
        domain_a = a.domain or "this domain"
        domain_b = b.domain or "another domain"
        if connection_type == "mechanism":
            return f"{domain_a} and {domain_b} are running the same mechanism."
        if connection_type == "analogical":
            return f"{a.title} and {b.title} are structural analogues across {domain_a} and {domain_b}."
        if connection_type == "inverse":
            return f"{a.title} and {b.title} are inverses — and the contrast clarifies both."
        return f"{a.title} and {b.title} touch in a way most people miss."
```

- [ ] **Step 4: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_two_atom_bridge.py -v
```

Expected: PASS both tests.

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/src/strategies/two_atom_bridge.py 01-projects/linkedin/tests/test_two_atom_bridge.py
git commit -m "feat(linkedin): two_atom_bridge strategy with typed-connection awareness"
```

---

### Task G3: `cluster_reveal` strategy

**Files:**
- Create: `01-projects/linkedin/src/strategies/cluster_reveal.py`
- Create: `01-projects/linkedin/tests/test_cluster_reveal.py`
- Create: `01-projects/linkedin/tests/fixtures/atoms/concepts/fourth-concept.md`
- Create: `01-projects/linkedin/tests/fixtures/atoms/concepts/fifth-concept.md`

- [ ] **Step 1: Add fixture atoms to form a tag-cluster of ≥4**

Create `01-projects/linkedin/tests/fixtures/atoms/concepts/fourth-concept.md`:

```markdown
---
title: Fourth Concept
type: concept
source_date: 2026-05-04
tags: [storytelling, character]
domain: writing
origin: test-fixture
---

A fourth concept tagged with storytelling.
```

Create `01-projects/linkedin/tests/fixtures/atoms/concepts/fifth-concept.md`:

```markdown
---
title: Fifth Concept
type: concept
source_date: 2026-05-05
tags: [storytelling, voice]
domain: writing
origin: test-fixture
---

A fifth concept tagged with storytelling.
```

- [ ] **Step 2: Write failing test**

```python
# tests/test_cluster_reveal.py
import pytest

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.cluster_reveal import ClusterReveal
from usage.atom_usage import AtomUsageTracker


def _ctx(atom_source, project_root):
    loader = AtomLoader(atom_source)
    return StrategyContext(
        loader=loader,
        graph=ConnectionGraph(loader.load_all()),
        atom_tracker=AtomUsageTracker(project_root / "state" / "atom-usage.json"),
    )


def test_cluster_reveal_finds_tag_cluster(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ClusterReveal()
    brief = strategy.generate_brief(ctx, {"cluster_anchor": "storytelling"})
    assert brief.strategy == "cluster_reveal"
    assert len(brief.atoms_used) >= 4


def test_cluster_reveal_too_small_fails(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ClusterReveal()
    with pytest.raises(ValueError, match="too small"):
        strategy.generate_brief(ctx, {"cluster_anchor": "nonexistent-tag"})
```

- [ ] **Step 3: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_cluster_reveal.py -v
```

Expected: FAIL.

- [ ] **Step 4: Implement `src/strategies/cluster_reveal.py`**

```python
"""cluster_reveal — name an emergent theme across ≥4 recently-captured atoms."""
from __future__ import annotations

import uuid
from datetime import datetime

from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import StrategyContext, eligible_atoms


class ClusterReveal:
    name = "cluster_reveal"
    MIN_CLUSTER_SIZE = 4

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        cluster_anchor = params.get("cluster_anchor")
        since = params.get("since")

        candidates = ctx.loader.load_all()
        if cluster_anchor:
            candidates = [a for a in candidates if cluster_anchor in a.tags and a.type != "connection"]
        elif since:
            since_date = since
            candidates = [
                a for a in candidates
                if a.type != "connection" and a.source_date and a.source_date >= since_date
            ]
        else:
            raise ValueError("cluster_reveal requires 'cluster_anchor' or 'since'")

        candidates = eligible_atoms(candidates, ctx.atom_tracker, role="primary")
        if len(candidates) < self.MIN_CLUSTER_SIZE:
            raise ValueError(
                f"Cluster too small: need ≥{self.MIN_CLUSTER_SIZE}, have {len(candidates)}"
            )

        candidates.sort(key=lambda a: a.source_date or "", reverse=True)
        chosen = candidates[: self.MIN_CLUSTER_SIZE + 2]

        theme = cluster_anchor or self._infer_theme(chosen)
        angle = (
            f"I keep capturing notes about {theme} without realizing. "
            f"Here's the pattern across {len(chosen)} of them."
        )

        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=f"{now.strftime('%Y-%m-%d')}-cluster-{theme.replace(' ', '-')}",
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={"cluster_anchor": cluster_anchor, "since": since, "theme": theme},
            atoms_used=[AtomRef(slug=a.slug, role="primary") for a in chosen],
            angle=angle,
            visual_tier="2_carousel",
            status=Status.DRAFTING,
            topic_tags=sorted({t for a in chosen for t in a.tags}),
        )

    def _infer_theme(self, atoms: list) -> str:
        from collections import Counter
        tag_counts = Counter(t for a in atoms for t in a.tags)
        if not tag_counts:
            return "an unnamed pattern"
        return tag_counts.most_common(1)[0][0]
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_cluster_reveal.py -v
```

Expected: PASS both tests.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/strategies/cluster_reveal.py 01-projects/linkedin/tests/test_cluster_reveal.py 01-projects/linkedin/tests/fixtures/atoms/concepts/
git commit -m "feat(linkedin): cluster_reveal strategy with theme inference"
```

---

### Task G4: `convergence_finder` strategy

**Files:**
- Create: `01-projects/linkedin/src/strategies/convergence_finder.py`
- Create: `01-projects/linkedin/tests/test_convergence_finder.py`
- Create: `01-projects/linkedin/tests/fixtures/atoms/concepts/security-trust.md`
- Create: `01-projects/linkedin/tests/fixtures/atoms/concepts/law-trust.md`
- Create: `01-projects/linkedin/tests/fixtures/atoms/concepts/child-trust.md`

- [ ] **Step 1: Add cross-domain atoms about a shared topic**

Create three concept atoms about "trust" across different domains:

`tests/fixtures/atoms/concepts/security-trust.md`:

```markdown
---
title: Security Trust Model
type: concept
source_date: 2026-05-06
tags: [trust, security]
domain: security
origin: test-fixture
---

Trust as a security primitive.
```

`tests/fixtures/atoms/concepts/law-trust.md`:

```markdown
---
title: Legal Trust
type: concept
source_date: 2026-05-06
tags: [trust, contracts]
domain: law
origin: test-fixture
---

Trust as a legal construct.
```

`tests/fixtures/atoms/concepts/child-trust.md`:

```markdown
---
title: Child Development Trust
type: concept
source_date: 2026-05-06
tags: [trust, development]
domain: psychology
origin: test-fixture
---

Trust as a developmental milestone.
```

- [ ] **Step 2: Write failing test**

```python
# tests/test_convergence_finder.py
import pytest

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.convergence_finder import ConvergenceFinder
from usage.atom_usage import AtomUsageTracker


def _ctx(atom_source, project_root):
    loader = AtomLoader(atom_source)
    return StrategyContext(
        loader=loader,
        graph=ConnectionGraph(loader.load_all()),
        atom_tracker=AtomUsageTracker(project_root / "state" / "atom-usage.json"),
    )


def test_finds_three_domains(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    brief = strategy.generate_brief(ctx, {"topic": "trust"})
    assert brief.strategy == "convergence_finder"
    domains = {ctx.loader.load_one(ref.slug).domain for ref in brief.atoms_used}
    assert len(domains) >= 3


def test_fails_when_no_convergence(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    with pytest.raises(ValueError, match="too narrow"):
        strategy.generate_brief(ctx, {"topic": "totally-unused-tag"})
```

- [ ] **Step 3: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_convergence_finder.py -v
```

Expected: FAIL.

- [ ] **Step 4: Implement `src/strategies/convergence_finder.py`**

```python
"""convergence_finder — find a topic touched by atoms across ≥3 distinct domains."""
from __future__ import annotations

import uuid

from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import StrategyContext, eligible_atoms


class ConvergenceFinder:
    name = "convergence_finder"
    MIN_DOMAINS = 3

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        topic = params.get("topic")
        if not topic:
            raise ValueError("convergence_finder requires 'topic' param")

        all_atoms = ctx.loader.load_all()
        topic_touchers = [
            a for a in all_atoms
            if a.type != "connection"
            and (topic in a.tags or topic in (a.title or "").lower() or topic in (a.body or "").lower())
        ]
        topic_touchers = eligible_atoms(topic_touchers, ctx.atom_tracker, role="primary")

        domain_to_atoms: dict[str, list] = {}
        for a in topic_touchers:
            if not a.domain:
                continue
            domain_to_atoms.setdefault(a.domain, []).append(a)

        if len(domain_to_atoms) < self.MIN_DOMAINS:
            raise ValueError(
                f"Atom corpus may be too narrow for '{topic}': "
                f"found {len(domain_to_atoms)} domain(s), need ≥{self.MIN_DOMAINS}"
            )

        chosen = []
        for domain, atoms in list(domain_to_atoms.items())[:self.MIN_DOMAINS]:
            atoms.sort(key=lambda a: len(ctx.graph.edges_for(a.slug)), reverse=True)
            chosen.append(atoms[0])

        domains = [a.domain for a in chosen]
        angle = (
            f"{topic.capitalize()} shows up in {', '.join(domains[:-1])}, "
            f"and {domains[-1]}. {len(chosen)} solutions to the same problem."
        )

        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=f"{now.strftime('%Y-%m-%d')}-convergence-{topic.replace(' ', '-')}",
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={"topic": topic, "domains": domains},
            atoms_used=[AtomRef(slug=a.slug, role="primary") for a in chosen],
            angle=angle,
            visual_tier="2_carousel",
            status=Status.DRAFTING,
            topic_tags=[topic],
        )
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_convergence_finder.py -v
```

Expected: PASS both tests.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/strategies/convergence_finder.py 01-projects/linkedin/tests/test_convergence_finder.py 01-projects/linkedin/tests/fixtures/atoms/concepts/
git commit -m "feat(linkedin): convergence_finder strategy for cross-domain topic posts"
```

---

## Phase H — Voice linter

### Task H1: Linter framework + rules.yml + hard-fail rules

**Files:**
- Create: `01-projects/linkedin/src/linter/__init__.py` (already exists, modify if empty)
- Create: `01-projects/linkedin/src/linter/rules.yml`
- Create: `01-projects/linkedin/src/linter/linter.py`
- Create: `01-projects/linkedin/tests/test_linter.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_linter.py
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
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_linter.py -v
```

Expected: FAIL.

- [ ] **Step 3: Write `src/linter/rules.yml`**

```yaml
hard_fail:
  em_dash:
    pattern: "—|–"
    message: "Em-dash or en-dash detected (CLAUDE.md §3)"
  contrastive_framing:
    pattern: "(?i)\\b(not (just |only |as )?[a-z][^.,;:]{1,40},?\\s+(but|but rather|but as)\\b)|(\\bnot [A-Za-z]+[+]\\b)"
    message: "Contrastive framing pattern (AI watermark)"
  exclamation_overflow:
    type: "ratio"
    per_words: 150
    max: 1
    message: ">1 exclamation per 150 words"
  word_count_extreme:
    type: "word_count"
    min: 30
    max: 600
    message: "Word count outside extreme bounds (<30 or >600); likely broken output"

soft_warn:
  ai_watermark_words:
    pattern: "(?i)\\b(delve|tapestry|navigate the complex|in conclusion|moreover|furthermore|in essence)\\b"
    message: "AI watermark vocabulary"
  word_count_target:
    type: "word_count_target"
    message: "Outside tier target range"
  passive_voice_excess:
    type: "passive_ratio"
    threshold: 0.20
    message: "Passive voice ratio above 20%"
```

- [ ] **Step 4: Implement `src/linter/linter.py`**

```python
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
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_linter.py -v
```

Expected: PASS all 5 tests.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/linter/ 01-projects/linkedin/tests/test_linter.py
git commit -m "feat(linkedin): voice linter with YAML rules (hard fails + soft warns)"
```

---

## Phase I — Text generator

### Task I1: Claude API text generator

**Files:**
- Create: `01-projects/linkedin/src/text_generator.py`
- Create: `01-projects/linkedin/tests/test_text_generator.py`

- [ ] **Step 1: Write failing test (with mocked Anthropic client)**

```python
# tests/test_text_generator.py
from unittest.mock import MagicMock

from atom_loader import AtomLoader
from models import AtomRef, PostBrief, Status, utc_now
from text_generator import TextGenerator


def _brief() -> PostBrief:
    now = utc_now()
    return PostBrief(
        id="b1",
        slug="2026-05-24-x",
        created_at=now,
        updated_at=now,
        strategy="source_spotlight",
        strategy_params={"source": "test-fixture"},
        atoms_used=[AtomRef(slug="sample-concept", role="primary")],
        angle="Three ideas all touch storytelling.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )


def test_generates_text(atom_source, mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Drafted post body. Word word word " * 30)]
    )
    loader = AtomLoader(atom_source)
    gen = TextGenerator(client=mock_client, loader=loader)
    brief = _brief()
    out = gen.generate(brief)
    assert "Drafted" in out.draft_text
    assert out.status.value == "text_ready"


def test_voice_rules_in_system_prompt(atom_source, mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="body " * 100)]
    )
    loader = AtomLoader(atom_source)
    gen = TextGenerator(client=mock_client, loader=loader)
    gen.generate(_brief())
    call_kwargs = mock_client.messages.create.call_args.kwargs
    system = call_kwargs.get("system", "")
    assert "em-dash" in system.lower() or "no em" in system.lower()
    assert "contrastive" in system.lower() or "not as x" in system.lower()
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_text_generator.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/text_generator.py`**

```python
"""Text generator — Claude API call constrained by voice rules."""
from __future__ import annotations

from typing import Any

from atom_loader import AtomLoader
from models import PostBrief, Status, utc_now


VOICE_SYSTEM_PROMPT = """You write LinkedIn posts in the author's voice.

HARD RULES (these are never broken):
- No em-dashes or en-dashes. Use commas, periods, or restructure.
- No contrastive framing patterns ("Not as X, but as Y", "Not just X, X+"). This is an AI watermark.
- No AI watermark vocabulary: "delve", "tapestry", "navigate the complex", "in conclusion", "moreover", "furthermore", "in essence".
- Active voice as default. Passive only when the subject is genuinely unknown.
- Maximum 1 exclamation point per 150 words.

POSITIONING:
- Framing is "insight + visible system". Posts can name "my second brain" or "the atom graph"
  as the source of the observation. The system is the differentiator.

VOICE:
- Observational, sharp, willing to be specific. Not promotional.
- Tight openings. No throat-clearing. No "In today's world..." or "Have you ever noticed...".
- One observation, evidence from the atoms, named takeaway.
- End with a question or an invitation when natural. No forced CTAs.

OUTPUT:
- Plain text only. No headers, no markdown.
- Target word count provided in the user prompt — stay in range.
"""


class TextGenerator:
    def __init__(self, client: Any, loader: AtomLoader, model: str = "claude-opus-4-7"):
        self.client = client
        self.loader = loader
        self.model = model

    def generate(self, brief: PostBrief, target_word_range: tuple[int, int] = (80, 200)) -> PostBrief:
        atom_summaries = []
        for ref in brief.atoms_used:
            atom = self.loader.load_one(ref.slug)
            if atom:
                snippet = (atom.body or "").strip().replace("\n", " ")[:240]
                atom_summaries.append(f"- [{atom.title}] ({atom.domain or 'no-domain'}): {snippet}")
        atoms_block = "\n".join(atom_summaries) or "(no atom summaries available)"

        lo, hi = target_word_range
        user_prompt = (
            f"Write a LinkedIn post advancing this angle:\n\n"
            f"  {brief.angle}\n\n"
            f"Use these atoms as substance:\n\n"
            f"{atoms_block}\n\n"
            f"Target word count: {lo}-{hi}.\n"
            f"Name 'my second brain' or 'the atom graph' as the source of the observation.\n"
            f"Plain text only — no markdown, no headers."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=VOICE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))

        brief.draft_text = text.strip()
        brief.status = Status.TEXT_READY
        brief.updated_at = utc_now()
        brief.status_history.append({
            "status": Status.TEXT_READY.value,
            "timestamp": brief.updated_at.isoformat(),
            "actor": "engine",
        })
        return brief
```

- [ ] **Step 4: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_text_generator.py -v
```

Expected: PASS both tests.

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/src/text_generator.py 01-projects/linkedin/tests/test_text_generator.py
git commit -m "feat(linkedin): text generator with voice-rule system prompt"
```

---

## Phase J — Tier 1 diagram renderer

### Task J1: DiagramRenderer (graphviz)

**Files:**
- Create: `01-projects/linkedin/src/renderers/base.py`
- Create: `01-projects/linkedin/src/renderers/diagram.py`
- Create: `01-projects/linkedin/tests/test_diagram_renderer.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_diagram_renderer.py
from pathlib import Path

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from models import AtomRef, PostBrief, Status, utc_now
from renderers.diagram import DiagramRenderer


def _brief() -> PostBrief:
    now = utc_now()
    return PostBrief(
        id="b1",
        slug="2026-05-24-diagram-test",
        created_at=now,
        updated_at=now,
        strategy="two_atom_bridge",
        strategy_params={"atom_a": "sample-concept", "atom_b": "third-concept", "connection_type": "analogical"},
        atoms_used=[
            AtomRef(slug="sample-concept", role="primary"),
            AtomRef(slug="third-concept", role="primary"),
        ],
        angle="A and B are doing the same job.",
        visual_tier="1_diagram",
        visual_brief={"diagram_layout": "bridge", "diagram_emphasis": "mechanism"},
        status=Status.GATE1_APPROVED,
    )


def test_render_writes_png(atom_source, project_root, brand_spec):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    renderer = DiagramRenderer(loader=loader, graph=graph, brand_spec_path=brand_spec)
    out_dir = project_root / "backlog" / "2026-05-24-diagram-test"
    out_dir.mkdir(parents=True)
    result = renderer.render(_brief(), out_dir)
    assert any(p.suffix == ".png" for p in result.asset_paths)
    assert all(Path(p).exists() for p in result.asset_paths)


def test_validate_rejects_too_many_nodes(atom_source, project_root, brand_spec):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    renderer = DiagramRenderer(loader=loader, graph=graph, brand_spec_path=brand_spec)
    brief = _brief()
    brief.atoms_used = [AtomRef(slug=f"atom{i}", role="primary") for i in range(7)]
    errors = renderer.validate(brief)
    assert any("more than 6 nodes" in e.lower() for e in errors)
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_diagram_renderer.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/renderers/base.py`**

```python
"""Renderer base — protocol + RenderResult."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import yaml

from models import PostBrief


@dataclass
class RenderResult:
    asset_paths: list[Path]
    cost: float = 0.0
    duration_s: float = 0.0
    logs: list[str] = field(default_factory=list)


class Renderer(Protocol):
    tier: int
    def validate(self, brief: PostBrief) -> list[str]: ...
    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult: ...


_YAML_BLOCK_RE = re.compile(r"```yaml\s*\n(.*?)\n```", flags=re.DOTALL)


def load_brand_spec(path: Path) -> dict[str, Any]:
    text = Path(path).read_text()
    m = _YAML_BLOCK_RE.search(text)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}
```

- [ ] **Step 4: Implement `src/renderers/diagram.py`**

```python
"""Tier 1 diagram renderer (graphviz)."""
from __future__ import annotations

import time
from pathlib import Path

import graphviz

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from models import PostBrief
from renderers.base import RenderResult, load_brand_spec


_EDGE_STYLE_BY_TYPE = {
    "mechanism": {"style": "solid", "penwidth": "2.5"},
    "analogical": {"style": "dashed", "penwidth": "1.5"},
    "causal": {"style": "solid", "penwidth": "1.8", "arrowhead": "vee"},
    "inverse": {"style": "solid", "penwidth": "1.5", "arrowhead": "diamond"},
    "compositional": {"style": "solid", "penwidth": "1.5"},
    "genealogical": {"style": "solid", "penwidth": "1.2"},
    "critique": {"style": "dashed", "penwidth": "1.5", "arrowhead": "tee"},
    "epistemic": {"style": "dotted", "penwidth": "1.5"},
    "general": {"style": "solid", "penwidth": "1.0"},
}


class DiagramRenderer:
    tier = 1

    def __init__(self, loader: AtomLoader, graph: ConnectionGraph, brand_spec_path: Path):
        self.loader = loader
        self.graph = graph
        self.brand = load_brand_spec(brand_spec_path)

    def validate(self, brief: PostBrief) -> list[str]:
        errors: list[str] = []
        n = len(brief.atoms_used)
        if n > 6:
            errors.append(f"Diagram cannot have more than 6 nodes (got {n})")
        if n < 1:
            errors.append("Diagram needs at least 1 node")
        return errors

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        start = time.time()
        errors = self.validate(brief)
        if errors:
            raise ValueError(f"Renderer validation failed: {errors}")
        out_dir.mkdir(parents=True, exist_ok=True)

        colors = self.brand.get("colors", {})
        typo = self.brand.get("typography", {})
        layout = self.brand.get("layout", {})

        dot = graphviz.Digraph(
            "linkedin_diagram",
            graph_attr={
                "bgcolor": colors.get("background", "#FFFFFF"),
                "pad": str(layout.get("padding", 24) / 24),
                "rankdir": "LR" if brief.visual_brief.get("diagram_layout") == "bridge" else "TB",
            },
            node_attr={
                "shape": "box",
                "style": "rounded,filled",
                "fillcolor": colors.get("background", "#FFFFFF"),
                "color": colors.get("accent_primary", "#1F1F1F"),
                "fontname": typo.get("body", "sans-serif"),
                "fontsize": str(typo.get("size_label", "11px")).replace("px", ""),
                "fontcolor": colors.get("text_primary", "#1F1F1F"),
                "margin": "0.2,0.1",
            },
            edge_attr={
                "color": colors.get("edge_default", "#737373"),
                "fontname": typo.get("body", "sans-serif"),
                "fontsize": str(typo.get("size_label", "11px")).replace("px", ""),
            },
        )

        slugs_in_brief = {ref.slug for ref in brief.atoms_used}
        for ref in brief.atoms_used:
            atom = self.loader.load_one(ref.slug)
            label = (atom.title if atom else ref.slug)
            dot.node(ref.slug, label=label)

        for edge in self.graph.edges:
            if edge.from_slug in slugs_in_brief and edge.to_slug in slugs_in_brief:
                style = _EDGE_STYLE_BY_TYPE.get(edge.connection_type, _EDGE_STYLE_BY_TYPE["general"])
                label = edge.connection_type if edge.connection_type != "general" else ""
                dot.edge(edge.from_slug, edge.to_slug, label=label, **style)

        png_path = out_dir / "diagram.png"
        svg_path = out_dir / "diagram.svg"
        dot.format = "png"
        dot.render(filename="diagram", directory=out_dir, cleanup=True)
        dot.format = "svg"
        dot.render(filename="diagram", directory=out_dir, cleanup=True)

        elapsed = time.time() - start
        return RenderResult(
            asset_paths=[png_path, svg_path],
            cost=0.0,
            duration_s=elapsed,
            logs=[f"Rendered {len(slugs_in_brief)} nodes in {elapsed:.2f}s"],
        )
```

- [ ] **Step 5: Run test to verify pass (requires `dot` binary)**

```bash
cd 01-projects/linkedin && which dot && pytest tests/test_diagram_renderer.py -v
```

Expected: PASS both tests. If `dot` is missing, run `brew install graphviz` first.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/renderers/ 01-projects/linkedin/tests/test_diagram_renderer.py
git commit -m "feat(linkedin): Tier 1 diagram renderer (graphviz) with brand-spec consumption"
```

---

## Phase K — linkedin-visual-discipline skill

### Task K1: Skill file + registry entry

**Files:**
- Create: `.claude/skills/linkedin/visual-discipline/SKILL.md`
- Modify: `03-skills/registry.md`

- [ ] **Step 1: Create directory and write SKILL.md**

```bash
mkdir -p /Users/gozzynwogbo/second-brain/.claude/skills/linkedin/visual-discipline
```

Write `.claude/skills/linkedin/visual-discipline/SKILL.md`:

```markdown
---
name: linkedin-visual-discipline
description: Use when rendering or reviewing LinkedIn post visuals (atom-graph diagrams, carousels, video). Enforces brand-spec consultation and anti-pattern checks. Triggers on `render visual`, `tier 1 diagram`, `review carousel`, `visual brief`, LinkedIn post bundle preparation.
when_to_use: Before any visual asset is committed to a LinkedIn post bundle. Also when reviewing an existing bundle for ship-readiness.
allowed-tools: Read, Bash, Glob
version: 1.0
scope: project
---

# LinkedIn Visual Discipline

## Purpose

Enforces visual quality discipline across LinkedIn post bundles. Two responsibilities:

1. **Brand-spec consultation.** No visual is allowed to drift from `01-projects/linkedin/brand-spec.md`. If the brand-spec changes, all subsequent renders adopt the change automatically.
2. **Anti-pattern enforcement.** Deterministic checks that block ship-readiness when violated.

## Trigger conditions

Fire automatically when:
- A renderer is about to write a visual asset to a backlog bundle.
- A `gate2_pending` bundle is being reviewed.
- User says "render the diagram", "make the carousel", "review the bundle".

## Required inputs

- `brief`: a PostBrief object (or its meta.json on disk).
- `brand_spec_path`: path to brand-spec.md (default: `01-projects/linkedin/brand-spec.md`).
- `bundle_dir`: target output directory.

## Protocol

1. **Load brand-spec.** Parse the YAML block. If missing or unparseable, halt and surface error.
2. **Validate brief against tier rules:**
   - Tier 1: ≤6 nodes, every node has ≥1 edge, aspect ratio 1:1 or 4:5.
   - Tier 2: ≤8 slides, ≤50 words/slide, ≤9 augmented images.
   - Tier 3: ≤12 total asset refs, ≤15s duration, 720p, body text always present.
3. **Run anti-pattern checks:**
   - No center-radial-gradient backgrounds.
   - No drop shadows on graph nodes.
   - No all-caps body labels.
   - No more than 6 atoms in a single diagram.
   - Connection-type edge labels mandatory when `connection_type ≠ general`.
   - No floating nodes (every node has ≥1 edge).
4. **Invoke renderer.** Pass brand tokens explicitly; renderer must not invent colors or fonts.
5. **Post-render verification.**
   - Output file(s) exist and are non-empty.
   - PNG dimensions match declared aspect ratio.
   - For tier 1: SVG also produced alongside PNG.
6. **Annotate bundle.** Write `01-projects/linkedin/backlog/<slug>/visual-checks.json` with check results.

## Anti-patterns (these are deterministic, not aesthetic preferences)

| Check | Why it matters |
|---|---|
| No center-radial-gradient | Generic AI aesthetic; instantly readable as generated |
| No drop shadows on nodes | Adds visual noise without information |
| No all-caps body labels | Reads as marketing-deck, not analytical |
| Max 6 nodes per diagram | Cognitive load; Miller's 7±2 minus margin |
| Edge labels when typed | Untyped edges are weakest connection-graph signal |
| Aspect ratio 1:1 or 4:5 | LinkedIn-feed display optimization |

## Examples

### Example 1 — Tier 1 diagram approval

Input: `brief` with 3 atoms, 2 typed connections, visual_tier=1_diagram.
Brand-spec: teal accent, Geist font.

Process:
1. Load brand-spec → confirm `colors.accent_primary` exists.
2. Validate: 3 nodes ✓, edge count ≥ nodes-1 ✓, aspect 1:1 ✓.
3. Anti-patterns: no shadows used ✓, labels mixed-case ✓.
4. Renderer outputs PNG + SVG.
5. Verify both files exist, PNG is 1080×1080 px.
6. Write checks file.

Output: `visual-checks.json` with `{"passed": true, "checks": [...]}`.

### Example 2 — Tier 1 rejection

Input: brief with 8 atoms.

Process:
1. Validate: 8 nodes > 6 → FAIL.
2. Return validation error before invoking renderer.

Output: error surfaced to user; renderer not invoked.

## Output contract

- On success: bundle directory contains the visual asset(s) and `visual-checks.json`.
- On failure: clear error message naming the failed check; renderer not invoked; bundle remains in pre-render state.
```

- [ ] **Step 2: Add row to `03-skills/registry.md`**

Find the appropriate category section (likely "LinkedIn" or "Design"; create a new "LinkedIn" section if absent). Append a row:

```markdown
| `linkedin-visual-discipline` | `.claude/skills/linkedin/visual-discipline/SKILL.md` | Visual quality enforcement for LinkedIn post bundles (brand-spec consultation + anti-pattern checks) | v1.0 | project | 2026-05-24 |
```

Match the existing column structure in `03-skills/registry.md`; adjust columns if the registry uses a different format.

- [ ] **Step 3: Verify the skill is discoverable**

```bash
cat /Users/gozzynwogbo/second-brain/.claude/skills/linkedin/visual-discipline/SKILL.md | head -10
grep -i "linkedin-visual" /Users/gozzynwogbo/second-brain/03-skills/registry.md
```

Expected: skill frontmatter visible; registry row visible.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/linkedin/visual-discipline/SKILL.md 03-skills/registry.md
git commit -m "feat(skills): linkedin-visual-discipline skill registered (project-scoped)"
```

---

## Phase L — CLI entry points + slash commands

### Task L1: `draft_post.py` CLI

**Files:**
- Create: `01-projects/linkedin/src/cli/draft_post.py`
- Create: `01-projects/linkedin/tests/test_cli_draft_post.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_cli_draft_post.py
import json
from unittest.mock import MagicMock, patch

from cli.draft_post import main


def test_main_invokes_strategy_writes_bundle(atom_source, project_root, brand_spec, monkeypatch):
    monkeypatch.setenv("LINKEDIN_ATOM_SOURCE", str(atom_source))
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("LINKEDIN_BRAND_SPEC", str(brand_spec))

    mock_anthropic = MagicMock()
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Generated post body. " * 30)]
    )

    with patch("cli.draft_post._make_anthropic_client", return_value=mock_anthropic):
        exit_code = main([
            "--strategy=two_atom_bridge",
            "--atom-a=sample-concept",
            "--atom-b=third-concept",
            "--no-render",
        ])

    assert exit_code == 0
    backlog = project_root / "backlog"
    assert any(p.is_dir() for p in backlog.iterdir())
    bundle = next(p for p in backlog.iterdir() if p.is_dir())
    meta = json.loads((bundle / "meta.json").read_text())
    assert meta["strategy"] == "two_atom_bridge"
    assert meta["status"] in ("text_ready", "drafting")
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_cli_draft_post.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/cli/draft_post.py`**

```python
"""/draft-post entry point."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional


def _make_anthropic_client():
    import anthropic
    return anthropic.Anthropic()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="draft-post")
    parser.add_argument("--strategy", default=None)
    parser.add_argument("--source", default=None)
    parser.add_argument("--atom-a", default=None)
    parser.add_argument("--atom-b", default=None)
    parser.add_argument("--topic", default=None)
    parser.add_argument("--cluster-anchor", default=None)
    parser.add_argument("--since", default=None)
    parser.add_argument("--tier", type=int, default=None)
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-render", action="store_true",
                        help="Skip rendering after text generation (for testing)")
    parser.add_argument("--advance", default=None, help="Advance bundle past Gate 1")
    parser.add_argument("--kill", default=None, help="Kill a bundle")
    parser.add_argument("--reason", default="", help="Required with --kill")
    parser.add_argument("--mark-posted", default=None, help="Mark bundle as posted")
    parser.add_argument("--url", default=None, help="Permalink for --mark-posted")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    atom_source = Path(os.environ.get("LINKEDIN_ATOM_SOURCE", "../../02-knowledge"))
    project_root = Path(os.environ.get("LINKEDIN_PROJECT_ROOT", "."))
    brand_spec = Path(os.environ.get("LINKEDIN_BRAND_SPEC", project_root / "brand-spec.md"))

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    if args.advance:
        return _advance(args.advance, project_root, brand_spec, atom_source, args)
    if args.kill:
        return _kill(args.kill, args.reason, project_root)
    if args.mark_posted:
        return _mark_posted(args.mark_posted, args.url, project_root)

    return _generate(args, atom_source, project_root, brand_spec)


def _generate(args, atom_source: Path, project_root: Path, brand_spec: Path) -> int:
    from atom_loader import AtomLoader
    from connection_graph import ConnectionGraph
    from storage.filesystem import FilesystemAdapter
    from state_log import StateLog
    from strategies.base import StrategyContext
    from strategies.source_spotlight import SourceSpotlight
    from strategies.two_atom_bridge import TwoAtomBridge
    from strategies.cluster_reveal import ClusterReveal
    from strategies.convergence_finder import ConvergenceFinder
    from text_generator import TextGenerator
    from usage.atom_usage import AtomUsageTracker
    from usage.connection_usage import ConnectionUsageTracker

    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    atom_tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json")
    conn_tracker = ConnectionUsageTracker(project_root / "state" / "connection-usage.json")
    ctx = StrategyContext(loader=loader, graph=graph, atom_tracker=atom_tracker, connection_tracker=conn_tracker)
    storage = FilesystemAdapter(project_root)
    state_log = StateLog(project_root / "logs" / "state.jsonl")

    strategies = {
        "source_spotlight": SourceSpotlight(),
        "two_atom_bridge": TwoAtomBridge(),
        "cluster_reveal": ClusterReveal(),
        "convergence_finder": ConvergenceFinder(),
    }
    strategy_name = args.strategy or "source_spotlight"
    if strategy_name not in strategies:
        print(f"Unknown strategy: {strategy_name}", file=sys.stderr)
        return 2

    params = {
        "source": args.source,
        "atom_a": args.atom_a,
        "atom_b": args.atom_b,
        "topic": args.topic,
        "cluster_anchor": args.cluster_anchor,
        "since": args.since,
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:
        brief = strategies[strategy_name].generate_brief(ctx, params)
    except ValueError as e:
        print(f"Strategy failed: {e}", file=sys.stderr)
        return 3

    if args.tier:
        brief.visual_tier = f"{args.tier}_{'diagram' if args.tier == 1 else 'carousel' if args.tier == 2 else 'video'}"

    if args.dry_run:
        print(f"DRY RUN — would generate brief for {brief.slug}: {brief.angle}")
        return 0

    storage.write(brief)
    state_log.record(brief.slug, "n/a", "drafting", actor="engine")

    client = _make_anthropic_client()
    gen = TextGenerator(client=client, loader=loader)
    brief = gen.generate(brief)
    storage.write(brief)
    state_log.record(brief.slug, "drafting", "text_ready", actor="engine")

    print(f"Wrote bundle: {project_root}/backlog/{brief.slug}/")
    return 0


def _advance(slug: str, project_root: Path, brand_spec: Path, atom_source: Path, args) -> int:
    from atom_loader import AtomLoader
    from connection_graph import ConnectionGraph
    from linter.linter import Linter
    from models import Status
    from renderers.diagram import DiagramRenderer
    from state_log import StateLog
    from storage.filesystem import FilesystemAdapter
    from usage.atom_usage import AtomUsageTracker
    from usage.approval_log import ApprovalLog

    storage = FilesystemAdapter(project_root)
    brief = storage.read(slug)
    text_path = project_root / "backlog" / slug / "text.md"
    approved_text = text_path.read_text().strip() if text_path.exists() else brief.draft_text
    brief.approved_text = approved_text

    annotations = Linter().lint(approved_text)
    hard_fails = [a for a in annotations if a.severity.value == "hard_fail"]
    if hard_fails and not args.force:
        print("Voice linter hard fails:", file=sys.stderr)
        for a in hard_fails:
            print(f"  - [{a.rule}] {a.message}", file=sys.stderr)
        print("Use --force to override.", file=sys.stderr)
        return 4

    state_log = StateLog(project_root / "logs" / "state.jsonl")
    brief.status = Status.GATE1_APPROVED
    storage.write(brief)
    state_log.record(slug, "text_ready", "gate1_approved", actor="user")

    if brief.visual_tier == "1_diagram":
        loader = AtomLoader(atom_source)
        graph = ConnectionGraph(loader.load_all())
        renderer = DiagramRenderer(loader=loader, graph=graph, brand_spec_path=brand_spec)
        out_dir = project_root / "backlog" / slug
        result = renderer.render(brief, out_dir)
        brief.visual_asset_paths = [str(p) for p in result.asset_paths]
        brief.status = Status.GATE2_PENDING
        storage.write(brief)
        state_log.record(slug, "gate1_approved", "gate2_pending", actor="engine")

    AtomUsageTracker(project_root / "state" / "atom-usage.json").mark_used(
        atom_slug=brief.atoms_used[0].slug, role="primary", post_id=brief.id
    )
    for ref in brief.atoms_used[1:]:
        AtomUsageTracker(project_root / "state" / "atom-usage.json").mark_used(
            atom_slug=ref.slug, role=ref.role, post_id=brief.id
        )

    ApprovalLog(project_root / "state" / "approvals.jsonl").record(
        post_id=brief.id,
        atoms_used=[r.slug for r in brief.atoms_used],
        strategy=brief.strategy,
        angle=brief.angle,
        draft_text=brief.draft_text,
        approved_text=approved_text,
        approved_visual_tier=1,
        tier_changed_at_gate1=False,
    )

    print(f"Advanced {slug} to {brief.status.value}")
    return 0


def _kill(slug: str, reason: str, project_root: Path) -> int:
    from models import Status
    from state_log import StateLog
    from storage.filesystem import FilesystemAdapter
    from usage.rejection_log import RejectionLog

    storage = FilesystemAdapter(project_root)
    brief = storage.read(slug)
    RejectionLog(project_root / "state" / "rejections.jsonl").record(
        post_id=brief.id,
        atoms_used=[r.slug for r in brief.atoms_used],
        strategy=brief.strategy,
        angle=brief.angle,
        draft_text=brief.draft_text,
        reason=reason,
        signal="killed_by_user",
    )
    brief.status = Status.REJECTED
    storage.write(brief)
    StateLog(project_root / "logs" / "state.jsonl").record(slug, "any", "rejected", actor="user", note=reason)
    print(f"Killed {slug}: {reason}")
    return 0


def _mark_posted(slug: str, url: str, project_root: Path) -> int:
    from models import Status
    from state_log import StateLog
    from storage.filesystem import FilesystemAdapter

    storage = FilesystemAdapter(project_root)
    brief = storage.read(slug)
    brief.published_url = url
    brief.status = Status.POSTED
    storage.write(brief)
    StateLog(project_root / "logs" / "state.jsonl").record(slug, "ready_to_post", "posted", actor="user", note=url or "")
    print(f"Marked posted: {slug} -> {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_cli_draft_post.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/src/cli/draft_post.py 01-projects/linkedin/tests/test_cli_draft_post.py
git commit -m "feat(linkedin): /draft-post CLI with generate, advance, kill, mark-posted"
```

---

### Task L2: `linkedin_status.py` CLI

**Files:**
- Create: `01-projects/linkedin/src/cli/linkedin_status.py`
- Create: `01-projects/linkedin/tests/test_cli_linkedin_status.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_cli_linkedin_status.py
import json
from datetime import datetime, timezone

from cli.linkedin_status import main
from models import AtomRef, PostBrief, Status, utc_now
from storage.filesystem import FilesystemAdapter


def test_backlog_lists_pending(project_root, monkeypatch, capsys):
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    storage = FilesystemAdapter(project_root)
    now = utc_now()
    brief = PostBrief(
        id="b1", slug="2026-05-24-pending",
        created_at=now, updated_at=now,
        strategy="source_spotlight", strategy_params={},
        atoms_used=[AtomRef(slug="a", role="primary")],
        angle="x", visual_tier="1_diagram",
        status=Status.TEXT_READY, draft_text="text",
    )
    storage.write(brief)
    exit_code = main(["--backlog"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "2026-05-24-pending" in out
    assert "text_ready" in out
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_cli_linkedin_status.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/cli/linkedin_status.py`**

```python
"""/linkedin-status entry point — read-only state surface."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="linkedin-status")
    parser.add_argument("--backlog", action="store_true")
    parser.add_argument("--ready", action="store_true")
    parser.add_argument("--cooldown", action="store_true")
    parser.add_argument("--rejections", action="store_true")
    parser.add_argument("--approvals", action="store_true")
    parser.add_argument("--last", type=int, default=10)
    args = parser.parse_args(argv)

    project_root = Path(os.environ.get("LINKEDIN_PROJECT_ROOT", "."))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from storage.filesystem import FilesystemAdapter

    storage = FilesystemAdapter(project_root)
    slugs = storage.list_slugs()

    def print_summary(filter_status: Optional[str] = None):
        for slug in slugs:
            try:
                brief = storage.read(slug)
            except Exception:
                continue
            if filter_status and brief.status.value != filter_status:
                continue
            print(f"  {slug:50s}  {brief.status.value:18s}  {brief.strategy}")

    if args.backlog:
        print("== Backlog (text_ready or gate2_pending) ==")
        for slug in slugs:
            try:
                brief = storage.read(slug)
            except Exception:
                continue
            if brief.status.value in ("text_ready", "gate2_pending"):
                print(f"  {slug:50s}  {brief.status.value:18s}  {brief.strategy}")
        return 0

    if args.ready:
        print("== Ready to post ==")
        print_summary(filter_status="ready_to_post")
        return 0

    if args.cooldown:
        usage_path = project_root / "state" / "atom-usage.json"
        if usage_path.exists():
            data = json.loads(usage_path.read_text())
            print("== Atom cooldown (most recent first) ==")
            for atom_slug, entries in sorted(data.items(), key=lambda kv: (kv[1][-1]["at"] if kv[1] else ""), reverse=True):
                if entries:
                    last = entries[-1]
                    print(f"  {atom_slug:40s}  last:{last['at']}  role:{last['role']}")
        else:
            print("(no atom usage yet)")
        return 0

    if args.rejections:
        path = project_root / "state" / "rejections.jsonl"
        if path.exists():
            lines = path.read_text().strip().splitlines()
            print(f"== Last {min(args.last, len(lines))} rejections ==")
            for line in lines[-args.last:]:
                entry = json.loads(line)
                print(f"  {entry['rejected_at']}  {entry['post_id']:30s}  {entry['rejection_signal']:20s}  reason: {entry.get('rejection_reason', '')[:60]}")
        return 0

    if args.approvals:
        path = project_root / "state" / "approvals.jsonl"
        if path.exists():
            lines = path.read_text().strip().splitlines()
            print(f"== Last {min(args.last, len(lines))} approvals ==")
            for line in lines[-args.last:]:
                entry = json.loads(line)
                mag = entry["edit_delta"]["magnitude"]
                print(f"  {entry['approved_at']}  {entry['post_id']:30s}  tier:{entry['approved_visual_tier']}  edit:{mag}")
        return 0

    print("== Full state report ==")
    print(f"Total bundles: {len(slugs)}")
    print()
    print_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_cli_linkedin_status.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/src/cli/linkedin_status.py 01-projects/linkedin/tests/test_cli_linkedin_status.py
git commit -m "feat(linkedin): /linkedin-status CLI with backlog/cooldown/rejection/approval views"
```

---

### Task L3: Slash command markdown wrappers

**Files:**
- Create: `.claude/commands/draft-post.md`
- Create: `.claude/commands/linkedin-status.md`

- [ ] **Step 1: Write `.claude/commands/draft-post.md`**

```markdown
---
description: Generate or transition a LinkedIn post draft from the second-brain atom graph
allowed-tools: Bash
---

# /draft-post

Generate or transition LinkedIn post drafts. See `01-projects/linkedin/docs/command-reference.md` for full flag reference.

## Behavior

When the user types `/draft-post [args]`:

1. **Resolve paths.** Set environment so the CLI knows where atoms, project, and brand-spec live:
   - `LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge`
   - `LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin`
   - `LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md`

2. **Invoke the Python CLI** with the user's flags appended:

   ```bash
   cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
   LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
   LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
   LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
   python -m cli.draft_post $ARGS
   ```

3. **After invocation:**
   - Read the bundle's `text.md` and `meta.json` from `01-projects/linkedin/backlog/<slug>/` to surface the result.
   - Report: the slug, the angle, the strategy used, and any voice-linter annotations.

## Conversational fallback

If the user gives natural-language instructions instead of flags (e.g., "kill the third one because the angle was too abstract"):
1. Read `01-projects/linkedin/backlog/` to identify the target slug.
2. Construct the equivalent `--kill <slug> --reason "..."` invocation.
3. Confirm the intended action with the user before running.

## Permission logging

This command writes state. Log to `01-projects/linkedin/logs/state.jsonl` (the CLI does this automatically) AND to `.claude/logs/system-events.jsonl` per CLAUDE.md §15. Include `reason` field.
```

- [ ] **Step 2: Write `.claude/commands/linkedin-status.md`**

```markdown
---
description: Read-only state surface for the LinkedIn content engine
allowed-tools: Bash, Read
---

# /linkedin-status

Read-only view of the LinkedIn engine state. See `01-projects/linkedin/docs/command-reference.md` for flags.

## Behavior

When the user types `/linkedin-status [args]`:

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
python -m cli.linkedin_status $ARGS
```

## Defaults

- Bare invocation: full state report (all bundles + their statuses).
- `--backlog`: only unreviewed drafts.
- `--cooldown`: atom cooldown picture.
- `--rejections [--last=N]`: recent rejections.
- `--approvals [--last=N]`: recent approvals with edit_delta magnitude.

## Read-only

This command does not write state. No permission_log entries required.
```

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/draft-post.md .claude/commands/linkedin-status.md
git commit -m "feat(linkedin): slash command markdown wrappers for draft-post and linkedin-status"
```

---

## Phase M — End-to-end integration test

### Task M1: End-to-end pipeline test

**Files:**
- Create: `01-projects/linkedin/tests/test_end_to_end.py`

- [ ] **Step 1: Write integration test**

```python
# tests/test_end_to_end.py
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from cli.draft_post import main as draft_post_main
from models import Status
from storage.filesystem import FilesystemAdapter


def test_full_pipeline_two_atom_bridge(atom_source, project_root, brand_spec, monkeypatch):
    """End-to-end: generate two_atom_bridge draft, advance through Gate 1, render diagram, mark posted."""
    monkeypatch.setenv("LINKEDIN_ATOM_SOURCE", str(atom_source))
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("LINKEDIN_BRAND_SPEC", str(brand_spec))

    mock_anthropic = MagicMock()
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text=(
            "Built a small engine this week that picks two atoms from my second brain "
            "and asks where they overlap. Surfaced a tie between feedback loops in "
            "auth design and feedback loops in pedagogy. Same gear, different machines. "
            "Wondering what other domains the same gear runs in. " * 2
        ))]
    )

    with patch("cli.draft_post._make_anthropic_client", return_value=mock_anthropic):
        # 1. Generate
        rc = draft_post_main([
            "--strategy=two_atom_bridge",
            "--atom-a=sample-concept",
            "--atom-b=third-concept",
        ])
        assert rc == 0

        # 2. Identify the bundle
        storage = FilesystemAdapter(project_root)
        slugs = storage.list_slugs()
        bundle_slug = next(s for s in slugs if "bridge" in s)
        brief = storage.read(bundle_slug)
        assert brief.status is Status.TEXT_READY
        assert (project_root / "backlog" / bundle_slug / "text.md").exists()

        # 3. Advance through Gate 1 (renders the diagram)
        rc = draft_post_main(["--advance", bundle_slug])
        assert rc == 0

        brief = storage.read(bundle_slug)
        assert brief.status is Status.GATE2_PENDING
        assert any(Path(p).exists() for p in brief.visual_asset_paths)

        # 4. Approvals log has an entry with edit_delta
        approvals_path = project_root / "state" / "approvals.jsonl"
        assert approvals_path.exists()
        entry = json.loads(approvals_path.read_text().strip())
        assert entry["edit_delta"]["magnitude"] in {"minor", "moderate", "major"}

        # 5. Atom usage tracker registered the atoms
        atom_usage = json.loads((project_root / "state" / "atom-usage.json").read_text())
        assert "sample-concept" in atom_usage
        assert "third-concept" in atom_usage

        # 6. Mark posted
        rc = draft_post_main(["--mark-posted", bundle_slug, "--url=https://linkedin.com/posts/x"])
        assert rc == 0
        brief = storage.read(bundle_slug)
        assert brief.status is Status.POSTED
        assert brief.published_url == "https://linkedin.com/posts/x"


def test_kill_flow(atom_source, project_root, brand_spec, monkeypatch):
    """Kill flow: generate, reject, verify rejection log + status."""
    monkeypatch.setenv("LINKEDIN_ATOM_SOURCE", str(atom_source))
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("LINKEDIN_BRAND_SPEC", str(brand_spec))

    mock_anthropic = MagicMock()
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text="text " * 100)]
    )

    with patch("cli.draft_post._make_anthropic_client", return_value=mock_anthropic):
        draft_post_main([
            "--strategy=two_atom_bridge",
            "--atom-a=sample-concept",
            "--atom-b=third-concept",
        ])
        storage = FilesystemAdapter(project_root)
        slug = next(s for s in storage.list_slugs() if "bridge" in s)

        rc = draft_post_main(["--kill", slug, "--reason=angle felt too generic"])
        assert rc == 0

        brief = storage.read(slug)
        assert brief.status is Status.REJECTED

        rejections = (project_root / "state" / "rejections.jsonl").read_text().strip().splitlines()
        assert any("generic" in json.loads(line)["rejection_reason"] for line in rejections)
```

- [ ] **Step 2: Run integration tests**

```bash
cd 01-projects/linkedin && which dot && pytest tests/test_end_to_end.py -v
```

Expected: PASS both tests. Requires `dot` (graphviz) binary.

- [ ] **Step 3: Commit**

```bash
git add -f 01-projects/linkedin/tests/test_end_to_end.py
git commit -m "test(linkedin): end-to-end integration tests for bridge + kill flows"
```

---

### Task M2: Smoke test against real atoms (manual)

This is a manual verification, not a pytest task.

- [ ] **Step 1: Verify Anthropic API key is set**

```bash
echo $ANTHROPIC_API_KEY | wc -c
```

Expected: >50 characters. If 1, set it: `export ANTHROPIC_API_KEY=sk-ant-...`.

- [ ] **Step 2: Generate a draft from real atoms**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
python -m cli.draft_post --strategy=source_spotlight --source="NotebookLM" --no-render
```

Expected: prints `Wrote bundle: .../backlog/<date>-<slug>/`. Inspect the resulting `text.md` and `meta.json`.

If `source_spotlight` complains about no atoms, switch source to one that exists in your vault (check `02-knowledge/` for `origin:` field values).

- [ ] **Step 3: Advance one bundle through Gate 1**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
python -m cli.draft_post --advance <slug-from-step-2>
```

Expected: prints `Advanced <slug> to gate2_pending`. PNG and SVG exist in the bundle folder.

- [ ] **Step 4: View status**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
python -m cli.linkedin_status --backlog
```

Expected: list of bundles with statuses.

- [ ] **Step 5: Open the rendered diagram**

```bash
open /Users/gozzynwogbo/second-brain/01-projects/linkedin/backlog/<slug>/diagram.png
```

Expected: a graphviz-rendered atom-graph diagram opens in Preview.

If the rendering looks broken (illegible labels, weird layout): file a follow-up note. Do not block v1.0 ship on aesthetic polish; the placeholder brand-spec is intentionally neutral. Real visual quality comes after the brand revamp lands.

- [ ] **Step 6: Document the smoke result**

Append a short note to `01-projects/linkedin/docs/decision-log.md` (create if missing):

```markdown
# Decision log

## 2026-05-24 — v1.0 smoke test
- First end-to-end run against real atoms.
- Strategy used: source_spotlight on source=<...>.
- Output: <slug> with diagram.png + diagram.svg.
- Voice linter result: <hard fails / clean>.
- Observations: <anything notable>.
```

---

## Self-review (run after writing this entire plan)

### Spec coverage check

| Spec section | Task(s) implementing it |
|---|---|
| §1 Goal & framing | (No task; framing is the design intent) |
| §2 Architecture | A1, A2, A3, A4, A5 (scaffold), all code tasks |
| §3 Data model | C1 (PostBrief), C2 (AtomLoader), C3 (ConnectionGraph) |
| §3.3 Hard guardrails | H1 (linter), J1 (diagram validator), L1 (CLI enforces them) |
| §4 Post-gen pipeline | G1-G4 (strategies), I1 (text gen), L1 (Gate 1 wiring) |
| §4.3 Voice linter | H1 |
| §4.4 Gate 1 | L1 (--advance) |
| §4.5 Atom selection guardrails | F1 (eligible_atoms), G1-G4 (per-strategy guardrails) |
| §5 Visual rendering layer | J1 (Tier 1); Tier 2 + Tier 3 are out of scope (separate plans) |
| §5.4 Skill harvest | K1 (visual-discipline only; Higgsfield/Remotion deferred to v1.1+) |
| §5.5 Brand spec external | A3 (placeholder), J1 (consumes brand-spec.md), L1 (env var) |
| §6 Operations + posting | L1 (--advance, --kill, --mark-posted), L2 (status surface), L3 (slash commands) |
| §6.4 Conversational interface | L3 (slash command markdown notes the conversational fallback) |
| §6.5 Logging | D2 (state log), E1 (cooldown), E2 (rejection + approval) |
| §6.6 Failure handling | L1 (--force, voice linter blocks unless overridden) |
| §9 Generation workflow + repetition | E1 (cooldowns), F1 (eligibility filter) |
| §9.5 Rejection + approval logging | E2 |
| §11 Connection-type taxonomy | B1 (atom-front-matter update) |

**Gaps identified and accepted:**
- Angle similarity check (§9.2 layer 4): NOT implemented in v1.0. Deferred to v1.1 because it requires embeddings infrastructure that doesn't yet exist. The other three anti-repeat layers (atom cooldown, connection cooldown, strategy diversity) cover most of the repeat risk for v1.0.
- Scoring function with weights (§9.4): NOT implemented in v1.0. Current selection is "first eligible" with light recency sort. Sophisticated scoring is v2.5 work driven by analytics. v1.0 is "pick eligible, let user judge."
- `--batch=N` and `--scan` modes: stubs exist in argument parser (L1) but only `--batch=1` (single) is wired. Batch implementation is straightforward extension; spec'd in command reference but deferred to v1.0.1 if needed.
- Strategy diversity bias (§9.2 layer 3): NOT implemented. User can override strategy via `--strategy=` flag, but auto-picker doesn't yet bias against recent strategies.

**Placeholder scan:** No `TBD`, `TODO`, or "implement later" found in step content. All code blocks contain runnable code.

**Type consistency check:** `PostBrief`, `Status`, `AtomRef`, `Atom`, `Edge`, `RenderResult`, `Annotation`, `Severity`, `StrategyContext` defined once and referenced consistently. CLI environment variables `LINKEDIN_ATOM_SOURCE`, `LINKEDIN_PROJECT_ROOT`, `LINKEDIN_BRAND_SPEC` used consistently in L1, L2, L3, M1, M2.

**Sequence sanity:** Each phase's tests depend only on prior-phase modules. No forward references.

---

## Execution handoff

Plan complete. Both parts saved:
- `01-projects/linkedin/docs/2026-05-24-v1-0-implementation-plan.md` — Phases A–F
- `01-projects/linkedin/docs/2026-05-24-v1-0-implementation-plan-part2.md` — Phases G–M (this file)

Two execution options:

**1. Subagent-Driven (recommended)** — A fresh subagent per task, review between tasks, fast iteration. Best for a multi-day build where each task can be verified independently.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints for review. Best if you want to watch the build happen turn-by-turn.

**Which approach?**

---

*End of Part 2.*
