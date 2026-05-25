# CLAUDE.md — LinkedIn Content Engine v1.0

> Implementation guide for the standalone LinkedIn content engine.
> This project generates posts from atoms stored in the second-brain vault.

---

## 1. Purpose

Generate LinkedIn posts from the atom graph in `02-knowledge/atoms/`. Each post is:
- Derived from a single atom
- Rendered via a reusable strategy (narrative, insight, thread, quick-take)
- Voice-checked against YAML rules before publishing
- Tracked for cooldown and usage limits
- Independently composable (extractable from the vault)

---

## 2. Project Structure

```
01-projects/linkedin/
├── CLAUDE.md               ← you are here
├── brand-spec.md           ← voice rules, tone, visual identity
├── src/
│   ├── strategies/         ← post rendering strategies (narrative, insight, etc.)
│   ├── renderers/          ← text rendering and formatting
│   ├── storage/            ← state persistence (JSON, YAML, SQLite)
│   ├── linter/             ← voice rule enforcement
│   ├── usage/              ← cooldown tracking and usage limits
│   ├── cli/                ← command-line interface
│   └── __init__.py
├── tests/                  ← pytest suite (required coverage: 80%+)
├── backlog/                ← feature queue and ideas
├── state/                  ← runtime state (posts, cooldowns, logs)
├── logs/                   ← execution logs
└── pyproject.toml          ← Python project metadata

```

---

## 3. Conventions

### Code

- **Language:** Python 3.11+
- **Type hints:** Pyright-strict mode. Every function signature must be annotated.
- **Voice rules:** Defined in YAML (brand-spec.md). Linter checks all generated text against rules.
- **Atom source:** Configurable path, defaults to `../../02-knowledge/atoms/` (relative to project root).
- **State:** Persisted via adapter pattern. Multiple backends supported (JSON, SQLite).
- **Storage:** Adapter abstraction. Swap implementations via config.

### Execution

- **CLI:** Single entry point at `src/cli/main.py`. All workflows routed through it.
- **Voice:** Every post passes through linter before rendering. Violations block generation.
- **Cooldown:** Atoms have min wait (in days) before re-selection. Enforced via storage.
- **Logging:** All operations logged to `logs/` with timestamp and outcome.

### Testing

- **Framework:** pytest
- **Coverage:** 80% minimum (enforced by pre-commit)
- **Fixtures:** Use conftest.py for shared state
- **Mocking:** Mock file I/O and external calls; never touch real atoms

### Branching

- Default: `main`
- Feature work: `feat/[feature-name]`
- Bug fixes: `fix/[bug-name]`
- Releases: Tag as `v[major].[minor].[patch]`

---

## 4. CLI Usage

```bash
# Generate a single post
python -m linkedin_engine generate --atom-id {atom_id} --strategy narrative

# Lint all atoms against voice rules
python -m linkedin_engine lint

# Show cooldown status
python -m linkedin_engine status --atom-id {atom_id}

# Reset cooldown for an atom (dev only)
python -m linkedin_engine reset-cooldown --atom-id {atom_id}

# Run all tests
pytest tests/
```

---

## 5. Testing Procedures

### Unit Tests
Each module under `src/` has a corresponding test file under `tests/`. Run with:
```bash
pytest tests/unit/
```

### Integration Tests
Cross-module workflows. Run with:
```bash
pytest tests/integration/
```

### Full Suite
```bash
pytest tests/ --cov=src/ --cov-fail-under=80
```

---

## 6. Voice Rules (brand-spec.md)

Voice rules are defined in YAML format. Example:

```yaml
rules:
  - name: "No jargon"
    pattern: "(?i)(synergy|leverage|paradigm shift)"
    action: "block"
    reason: "Avoid corporate clichés"

  - name: "Max 280 chars per sentence"
    pattern: "^.{281,}$"
    action: "block"
    reason: "Keep sentences readable"

  - name: "At least one emoji per post"
    pattern: "\\p{Emoji}"
    action: "require"
    reason: "Visual variety"
```

The linter checks all generated text against these rules. Violations are reported with location and fix suggestions.

---

## 7. Key Technical Decisions

### Atom Source Isolation
Atom source path is **configurable** at runtime. This allows:
- Dev: point to local test atoms
- Prod: point to vault atoms
- Testing: use fixtures without touching real files

Default path is `../../02-knowledge/atoms/` but can be overridden via environment variable or config file.

### PostBrief Abstraction
Intermediate representation between atom selection and rendering:
```python
@dataclass
class PostBrief:
    atom_id: str
    strategy: str  # "narrative", "insight", "thread", "quick-take"
    text: str
    metadata: dict
```

This decouples atom selection from rendering. Strategies consume PostBrief, not raw atoms.

### State Persistence
Adapter pattern allows multiple backends without code changes:
```python
class StorageAdapter(ABC):
    @abstractmethod
    def save_post(self, post_brief: PostBrief) -> None: ...
    @abstractmethod
    def get_cooldown(self, atom_id: str) -> int: ...
```

---

## 8. Development Workflow

1. **Create a feature branch:** `git checkout -b feat/your-feature`
2. **Implement feature** in `src/`
3. **Write tests** in `tests/`
4. **Run linter:** `pylint src/`
5. **Run tests:** `pytest tests/ --cov=src/`
6. **Commit:** Follow conventional commits (feat/fix/docs/test/refactor)
7. **Open PR** against main
8. **Merge when passing CI/CD**

---

## 9. Deployment

Deployments are triggered by git tags on `main`:
```bash
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

---

## 10. Open Questions

- [ ] How should voice rules be versioned?
- [ ] Should cooldown be global or per-strategy?
- [ ] Do we need multi-tenant state isolation?

---

*Last updated: 2026-05-25*
