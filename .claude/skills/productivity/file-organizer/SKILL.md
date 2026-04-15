# Skill: file-organizer

Organize files and folders by auditing contents, finding duplicates, proposing clean structures, and executing bulk moves with safety checks.
Trigger phrases: "organize my downloads", "clean up this folder", "find duplicate files", "restructure this directory", "archive old files".
Output artifact: reorganized directory structure with `_review/` folder for flagged items.

---

# File Organizer

Intelligently organize files by understanding context, finding duplicates, and creating clean structures.

## When to Use

- Cleaning up a messy downloads folder or desktop
- Reorganizing a project directory
- Finding and removing duplicate files
- Creating a folder structure for a new project
- Archiving old files systematically

## Process

### Step 1: Audit

```bash
# List directory with sizes and dates
ls -lh ~/Downloads | sort -k5 -rh

# Show directory tree (2 levels)
find . -maxdepth 2 -type d | sort

# Find large files
find . -size +100M -type f

# Find duplicates by name
find . -name "*.pdf" | sort
```

### Step 2: Understand the Content

Before reorganizing, understand what's there:
- What types of files? (docs, images, code, archives)
- What time period? (recent vs. old)
- What projects or topics?
- What's actively used vs. archivable?

### Step 3: Propose a Structure

Present a proposed structure to the user **before** moving anything:

```
proposed/
├── active/
│   ├── [project-name]/
│   └── [project-name]/
├── archive/
│   └── [year]/
├── reference/
│   ├── docs/
│   └── media/
└── inbox/           <- unsorted items
```

Get confirmation before executing.

### Step 4: Execute

```bash
# Create structure
mkdir -p organized/{active,archive/2024,reference/docs,inbox}

# Move files (use mv, not cp, to avoid duplicates)
mv important-doc.pdf organized/reference/docs/

# Batch move by type
find . -name "*.pdf" -maxdepth 1 -exec mv {} organized/reference/docs/ \;

# Batch move by date
find . -newer 2024-01-01 -maxdepth 1 -type f -exec mv {} organized/active/ \;
```

### Step 5: Find and Handle Duplicates

```bash
# Find files with identical names
find . -name "*.docx" | sort | uniq -d

# Find files with identical content (using md5)
find . -type f | xargs md5sum | sort | awk 'seen[$1]++ {print $2}' > duplicates.txt
cat duplicates.txt
```

For each duplicate:
- Keep the one in the most logical location
- Move others to a `_review/` folder before deleting (safety buffer)

## Naming Conventions

Suggest consistent naming to prevent future chaos:

| Pattern | Example |
|---------|---------|
| Dated files | `2025-02-20-meeting-notes.md` |
| Project files | `[project]-[type]-[version].ext` |
| Invoices | `invoice-[vendor]-[YYYY-MM].pdf` |
| Screenshots | `screenshot-[description]-[YYYY-MM-DD].png` |

## Safety Rules

- **Never delete without review** -- move to `_review/` first
- **Always confirm before bulk operations**
- **Keep a log of what was moved** where possible
- **Don't reorganize files that are actively in use** by other apps (e.g., app config files)
