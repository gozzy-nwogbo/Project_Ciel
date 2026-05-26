#!/usr/bin/env python3
"""Recap atoms whose tldr field was truncated by the v1.1.1 safety net.

v1.1.1 introduced a hard 80-char cap on TldrFiller output. When the LLM
overshot, the safety net cut the response at a word boundary and appended
'…'. The truncated tldr was then back-written to the atom file. When the
v1.2 renderer reads such an atom, it ships the truncated string into the
visual where it reads as an incomplete sentence.

This script scans 02-knowledge/ for atoms with tldrs ending in '…' or '...',
clears the tldr field, and re-runs TldrFiller (with the tighter v1.2.1 prompt
that targets 60 chars instead of 80). The Filler's back-write logic writes
the new tldr in place.

Run from the linkedin project root:
    ./bin/draft-post does not invoke this — it's a one-off maintenance pass.
    Run directly: PYTHONPATH=src python3 scripts/recap_tldrs.py [--dry-run]

Cost: ~$0.001 per atom with Haiku. Cheap.

Known limitation (v1.2.1): even with the tightened SYSTEM_PROMPT targeting 60
chars, Haiku frequently overshoots 80 chars and the safety net cuts with '…'.
The script reports those as 'ok' because the filler returned text, but the
resulting tldr is still truncated. v1.2.2 follow-up: add retry-on-overshoot
loop to TldrFiller (re-ask for <50 chars if first response triggers the
safety-net cut). Until then, hand-fix the output if you see '…' endings.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="recap-tldrs")
    parser.add_argument(
        "--atom-source",
        default=os.environ.get(
            "LINKEDIN_ATOM_SOURCE", "/Users/gozzynwogbo/second-brain/02-knowledge"
        ),
        help="Path to the atom corpus (default: $LINKEDIN_ATOM_SOURCE or vault default).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List affected atoms but do not regenerate or back-write.",
    )
    args = parser.parse_args(argv)

    # Ensure src/ is on the path so we can import the engine modules.
    here = Path(__file__).resolve().parent
    src = (here.parent / "src").resolve()
    sys.path.insert(0, str(src))

    from atom_loader import AtomLoader
    from sources.tldr_filler import TldrFiller

    loader = AtomLoader(Path(args.atom_source))
    atoms = loader.load_all()
    affected = [a for a in atoms if a.tldr and (a.tldr.endswith("…") or a.tldr.endswith("..."))]

    print(f"Scanned {len(atoms)} atoms; {len(affected)} have truncated tldrs.")
    for a in affected:
        print(f"  - {a.slug}: {a.tldr!r}")

    if args.dry_run:
        print("\n--dry-run: nothing changed.")
        return 0
    if not affected:
        return 0

    print(f"\nRegenerating {len(affected)} tldrs via TldrFiller (Haiku)...")

    import anthropic

    client = anthropic.Anthropic()
    filler = TldrFiller(client=client)

    succeeded = 0
    failed: list[str] = []
    for atom in affected:
        # Clear the old tldr so the in-memory object reflects the regeneration target.
        # (The atom file on disk is overwritten by TldrFiller.fill on success.)
        atom.tldr = None
        new_tldr = filler.fill(atom)
        if new_tldr:
            print(f"  ok  {atom.slug}: {new_tldr!r}")
            succeeded += 1
        else:
            print(f"  FAIL {atom.slug}: filler returned None", file=sys.stderr)
            failed.append(atom.slug)

    print(f"\nDone. {succeeded} repaired, {len(failed)} failed.")
    if failed:
        print(f"Failed slugs: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
