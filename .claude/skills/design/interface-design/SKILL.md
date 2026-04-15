# Skill: Interface Design

Principle-based UI design engineering with session memory and design system persistence.
Trigger: "build interface", "design UI", "interface design", "design system", "dashboard layout"
Output artifact: .interface-design/system.md (persisted design system)

---

# Interface Design

**Craft - Memory - Consistency**

Build interfaces with intention. Remember decisions across sessions. Maintain systematic consistency.

*For interface design — dashboards, apps, tools, admin panels. Not for marketing sites.*

## When to Use

- Building any UI component, page, or interface in Claude Code
- When design consistency across a project matters
- When picking up UI work from a previous session
- Auditing existing code against an established design system

## How It Works

### Session Start

**If `.interface-design/system.md` exists in the project:**
1. Load and apply the saved design system automatically
2. State which patterns are being applied before building
3. Offer to save any new patterns introduced

**If no system.md exists:**
1. Assess project context (dark/light, density, audience)
2. Propose a design direction and confirm with user
3. State explicit design choices before each component
4. Build with consistent principles throughout
5. Offer to save the system for future sessions

### Design Directions

| Direction | Feel | Best For |
|---|---|---|
| **Precision & Density** | Tight, technical, monochrome | Developer tools, admin dashboards |
| **Warmth & Approachability** | Generous spacing, soft shadows | Collaborative tools, consumer apps |
| **Sophistication & Trust** | Cool tones, layered depth | Finance, enterprise B2B |
| **Boldness & Clarity** | High contrast, dramatic space | Modern dashboards, data-heavy apps |
| **Utility & Function** | Muted, functional density | GitHub-style tools |
| **Data & Analysis** | Chart-optimized, numbers-first | Analytics, BI tools |

### Depth Strategies

- **Borders-only**: Clean technical feel — `rgba(255,255,255,0.06)` borders, no shadows
- **Subtle elevation**: Layered lightness scale (7% → 9% → 11%)
- **Shadow-based**: Classic depth with box-shadows

### Spacing

Always work on a grid. Default: 4px base scale (4, 8, 12, 16, 24, 32, 48, 64).

### Before Building Each Component

State the design choices being applied:
```
Depth: borders-only
Surfaces: 7% → 9% lightness scale
Spacing: 8px base
Border radius: 6px buttons, 8px cards
Typography: 14px body, 12px secondary
```

## Commands

```
/interface-design:init       # Start fresh session with design principles
/interface-design:status     # Show current system state
/interface-design:audit      # Check existing code against system
/interface-design:extract    # Extract patterns from existing code
```

## System File Format

Decisions are saved to `.interface-design/system.md`:

```markdown
# Design System

## Direction
Personality: Precision & Density
Foundation: Cool (slate)
Depth: Borders-only

## Tokens
### Spacing
Base: 4px
Scale: 4, 8, 12, 16, 24, 32

### Colors
--foreground: slate-900
--secondary: slate-600
--accent: blue-600

## Patterns
### Button Primary
- Height: 36px
- Padding: 12px 16px
- Radius: 6px

### Card Default
- Border: 0.5px solid rgba(255,255,255,0.06)
- Padding: 16px
- Radius: 8px
```

## Philosophy

- **Decisions compound** — a spacing value chosen once becomes a pattern
- **Consistency beats perfection** — a coherent system with "imperfect" values beats a scattered interface with "correct" ones
- **Memory enables iteration** — when you can see what you decided and why, you evolve intentionally instead of drifting
