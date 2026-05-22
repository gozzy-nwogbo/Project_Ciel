# /deep-parse-staging

Deep-parse the files in `00-inbox/staging/` that Haiku already shallow-processed via the flush cron. Catches durable atoms Haiku missed due to its 15k-char truncation and single-shot extraction. This command writes to `02-knowledge/` and moves sources to `00-inbox/archived/`.

SESSION TYPE: reflect

---

## When to run

Invoke this when staging has accumulated files (typically prompted by the session-start reminder set up by `.claude/scripts/check-staging.py`). Manual runs are fine any time staging has unprocessed clippings.

---

## Pre-flight reads

Before parsing, read:
- `CLAUDE.md` Sections 6 (session types), 14 (knowledge pipeline), 10 (token efficiency)
- `01-projects/open-brain/notes/phase-6.5-data-routing-layer.md` — confirms no Supabase writes this session
- `02-knowledge/index.md` (or skim folder list via `ls 02-knowledge/`) — for duplicate-detection priming

---

## Parse protocol

For each file in `00-inbox/staging/*.md`:

### Step 1: Classify the source

Open the file. From frontmatter + first 1000 chars, classify as:

- **DEEP** — long-form research, talks, retrospectives, technical breakdowns by domain experts (e.g., Nate B Jones, Reddit founder threads, platform-engineering retros)
- **LIGHT** — tutorial walkthroughs with implementation steps. Output goes to project notes, not 02-knowledge/
- **SKIP** — sponsored content, affiliate-link-heavy material, sales copy disguised as content. Flag indicators: "sponsored by", affiliate URLs in description, "promo code", "use my link", gumroad/skool upsells dominating intro

### Step 2: Process by class

**DEEP:**
1. Read the entire file (use offset/limit on Read if it exceeds 25k tokens)
2. Identify durable claims, ignoring source-specific implementation detail
3. For each candidate atom, grep `02-knowledge/` for similar existing atoms BEFORE writing (search likely kebab-case filenames and key phrases)
4. Write only the net-new claims. Skip duplicates.
5. Write atoms to the appropriate `02-knowledge/[topic]/` subfolder following the existing frontmatter format (type/source_date/tags + 2-3 sentence single-claim body)
6. Where a new atom connects two existing atoms, write a connection file in `02-knowledge/connections/`

**LIGHT:**
1. Skim (~first third, then jump to chapter markers)
2. Surface project-relevant patterns to an appropriately-named notes file under `01-projects/[relevant-project]/notes/`. Default project: `open-brain` for AI-OS / agent / workflow tutorials.
3. Do NOT write atoms — tutorial takeaways are not durable knowledge.

**SKIP:**
1. Write nothing.
2. Note the reason (sponsored / affiliate-heavy / substantiated overlap already covered).
3. Archive anyway.

### Step 3: Archive

After processing, move the source from `00-inbox/staging/` to `00-inbox/archived/` (create the directory if missing). Use `mv` via Bash.

### Step 4: Session log

Append a Session block to `06-daily/[YYYY-MM-DD].md` with:
- Summary of files processed (1 paragraph)
- Atoms written, organized by destination folder
- Connections written
- Per-file extraction tally (table: source | atoms | connections | notes)
- Decisions made and why
- Files moved

### Step 5: Clear the reminder

Run:
```bash
rm -f .claude/reminders/deep-parse-due.md
```

---

## Hard rules

1. **No Supabase writes.** Phase 6.5 is unresolved. Filesystem only.
2. **Check duplicates before writing.** Grep against existing atom filenames + key phrases. Skip if covered.
3. **No em-dashes, no AI watermarks** in atom prose (CLAUDE.md Section 3).
4. **No forced extraction.** If a source has no durable insight, skip-with-note and archive. Do not invent atoms.
5. **Permission logging.** Filesystem only — no MCP tool calls expected. If MCP tools are invoked, follow CLAUDE.md Section 15.
6. **Atom format:** frontmatter (title, type, source_date, tags) + single-claim body 2-3 sentences. Match existing atoms in target folder.
7. **Connection format:** frontmatter (title, type=connection, from, to, source_date) + "**From** -> **To**" arrow + 1-sentence relationship.

---

## Expected output shape

- N atoms written (could be 0 to 30, depends on what's in staging)
- M connections written
- Possible project-notes files for LIGHT-parsed tutorials
- All staging sources moved to archived/
- Session log appended
- `.claude/reminders/deep-parse-due.md` removed

---

## How to start

1. Read the three docs above.
2. List staging contents: `ls 00-inbox/staging/`.
3. For each file: classify, process per its class, archive.
4. Write session log.
5. Remove reminder file.
