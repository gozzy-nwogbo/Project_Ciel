# Skill: meeting-insights-analyzer

Analyze meeting transcripts for behavioral patterns (speaking ratios, conflict avoidance, filler words, leadership dynamics, decision quality) beyond simple summaries.
Trigger phrases: "analyze this meeting", "meeting insights", "review this transcript", "meeting dynamics", "who talked the most".
Output artifact: meeting analysis report at `01-projects/[project]/output/writing/meeting-analysis-[date].md`.

---

# Meeting Insights Analyzer

Analyzes meeting transcripts for behavioral patterns, not just content -- speaking ratios, conflict avoidance, filler words, leadership dynamics.

## When to Use

- After receiving a meeting transcript (Zoom, Otter.ai, Fireflies, etc.)
- Coaching a leader on their meeting facilitation style
- Analyzing recurring team meetings for dysfunction patterns
- Preparing feedback on how a meeting was run
- Understanding why a meeting felt unproductive

## Analysis Framework

### 1. Speaking Time Distribution

Calculate and report approximate speaking time by participant:
```
Participant analysis:
- [Name]: ~40% of speaking time (dominant voice)
- [Name]: ~30%
- [Name]: ~20%
- [Name]: ~10% (under-represented)
```

Flag: Any participant at <5% in a meeting they're expected to contribute to.

### 2. Conflict Avoidance Patterns

Look for:
- Immediate topic changes after disagreement
- Hedging language: "maybe", "sort of", "kind of", "I could be wrong but"
- Passive agreement: "sure", "whatever works", "that's fine"
- Questions deflected instead of answered

Report: Moments where productive tension was avoided.

### 3. Filler Word Analysis

Count and flag overuse of:
- "um", "uh", "like", "you know", "basically", "literally"
- "kind of", "sort of", "maybe" (when used for softening, not genuine uncertainty)

Report top filler patterns per speaker if notable.

### 4. Decision Quality

For each decision made (or avoided):
- Was the decision clearly stated?
- Was an owner assigned?
- Was a deadline given?
- Was it documented or left implicit?

Template:
```
| Decision | Owner | Deadline | Clarity |
|----------|-------|----------|---------|
| [topic]  | [person] | [date/none] | Clear/Partial/Missing |
```

### 5. Leadership Style Signals

Observe the meeting facilitator/leader for:
- **Inquiry vs. advocacy**: Do they ask questions or push their own view?
- **Airtime management**: Do they draw out quieter voices?
- **Closure**: Do discussions reach conclusions, or trail off?
- **Psychological safety cues**: How is disagreement received?

### 6. Action Item Extraction

List every commitment made:
```
| Action | Owner | Deadline |
|--------|-------|----------|
| [what] | [who] | [when] |
```

Flag any action mentioned without a clear owner or deadline.

## Output Format

```markdown
## Meeting Analysis: [Meeting Title / Date]
**Duration**: [X minutes] | **Participants**: [N people]

### Key Takeaways
[3-5 bullet observations worth acting on]

### Speaking Distribution
[Table or bar-style summary]

### Decision Quality
[Table of decisions made]

### Action Items
[Table of commitments]

### Behavioral Patterns
[Notable dynamics -- conflict avoidance, dominant voices, etc.]

### Recommendations
[1-3 specific suggestions for improving future meetings]
```

## Limitations

- Analysis is based on text only -- tone and non-verbals are not captured
- Speaking time estimates from transcripts are approximate
- Context about relationships and history matters -- flag when interpretation is uncertain
