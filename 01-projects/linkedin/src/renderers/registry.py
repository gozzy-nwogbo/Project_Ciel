"""Tier 1 renderer registry. Strategy name to renderer instance dispatch."""
from __future__ import annotations

from typing import Any

from renderers.atom_card import AtomCardRenderer
from renderers.bridge_card import BridgeCardRenderer
from renderers.convergence_card import ConvergenceCardRenderer


_TIER1_CLASSES: dict[str, type] = {
    "source_spotlight":   AtomCardRenderer,
    "two_atom_bridge":    BridgeCardRenderer,
    "convergence_finder": ConvergenceCardRenderer,
}


def for_strategy(strategy_name: str, **kwargs: Any):
    cls = _TIER1_CLASSES.get(strategy_name)
    if cls is None:
        raise ValueError(f"No Tier 1 renderer for strategy '{strategy_name}'")
    return cls(**kwargs)
