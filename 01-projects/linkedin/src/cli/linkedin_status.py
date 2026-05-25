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
