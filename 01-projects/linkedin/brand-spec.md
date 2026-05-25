# Brand Spec — LinkedIn Engine Extension

**Inherits from:** `02-knowledge/brand-spec.md` (vault-level brand spec, v3.0)
**Purpose:** Renderer-specific tokens for LinkedIn post visuals (network graphs, cards).

All base tokens (colors, typography, spacing, voice) come from the vault-level spec.
This file adds only what the LinkedIn engine's visual renderers need beyond the base.

---

## Renderer Tokens

```yaml
colors:
  # Inherited from base spec
  accent_primary:    "#B5654A"     # muted terracotta (from base)
  background:        "#FAF8F5"     # warm cream (from base)
  text_primary:      "#2C2825"     # warm dark gray (from base)
  text_secondary:    "#6B6560"     # muted (from base)

  # Graph-specific
  edge_default:      "#6B6560"     # text_secondary
  edge_mechanism:    "#2C2825"     # text_primary
  edge_analogical:   "#9C9590"     # text_tertiary, rendered dashed
  node_fill:         "#F3F0EB"     # surface_subtle
  node_border:       "#E8E4DF"     # border

typography:
  body: "Geist, system-ui, -apple-system, sans-serif"
  mono: "Geist Mono, ui-monospace, monospace"
  size_body: "14px"
  size_label: "11px"
  size_title: "18px"

layout:
  aspect_ratios: ["1:1", "4:5"]
  padding: 32
  node_padding: 12
  edge_thickness_default: 1.5
  edge_thickness_emphasis: 2.5

anti_patterns:
  - "no center-radial-gradient backgrounds"
  - "no drop shadows on nodes"
  - "no all-caps labels"
  - "minimum 16px between adjacent nodes"
```

---

## Notes

- All renderers read tokens from this file for graph-specific values.
- For base brand decisions (accent color, voice rules, typography family), defer to `02-knowledge/brand-spec.md`.
- If a renderer needs a token not listed here, check the base spec first before inventing one.
