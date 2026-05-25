# Brand Spec — PLACEHOLDER

**Status:** Placeholder for v1.0. Will be replaced by brand revamp workstream output.

## Tokens

```yaml
colors:
  accent_primary: "#1F1F1F"     # placeholder neutral
  accent_secondary: "#737373"
  background: "#FFFFFF"
  edge_default: "#737373"
  edge_mechanism: "#1F1F1F"
  edge_analogical: "#737373"    # dashed
  text_primary: "#1F1F1F"
  text_secondary: "#525252"

typography:
  body: "system-ui, -apple-system, sans-serif"
  display: "system-ui, -apple-system, sans-serif"
  mono: "ui-monospace, monospace"
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

## Notes

Once the brand revamp workstream completes, replace this file (or symlink it) to the brand revamp output. All renderers read tokens from this file; nothing in code hardcodes brand decisions.
