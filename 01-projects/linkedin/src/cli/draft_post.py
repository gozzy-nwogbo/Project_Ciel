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
        validation_errors = renderer.validate(brief)
        edgeless = any("edgeless" in e.lower() for e in validation_errors)
        if edgeless and not args.force:
            print(
                "WARNING: Tier 1 diagram skipped — no connection atoms exist among the chosen atoms.",
                file=sys.stderr,
            )
            print(
                "  Bundle advanced to gate2_pending without a visual. Use --force to render anyway.",
                file=sys.stderr,
            )
            brief.visual_asset_paths = []
            brief.status = Status.GATE2_PENDING
            storage.write(brief)
            state_log.record(slug, "gate1_approved", "gate2_pending", actor="engine", note="edgeless_tier1_skipped")
        else:
            result = renderer.render(brief, out_dir)
            brief.visual_asset_paths = [str(p) for p in result.asset_paths]
            brief.status = Status.GATE2_PENDING
            storage.write(brief)
            state_log.record(slug, "gate1_approved", "gate2_pending", actor="engine")
    else:
        # Text-only tiers (0_text, etc.) skip rendering and advance directly to Gate 2.
        brief.visual_asset_paths = []
        brief.status = Status.GATE2_PENDING
        storage.write(brief)
        state_log.record(slug, "gate1_approved", "gate2_pending", actor="engine", note=f"text_only_tier_{brief.visual_tier}")

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
