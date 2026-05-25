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
