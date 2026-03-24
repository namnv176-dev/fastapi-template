---
description: Generate a daily log of changes and decisions made in the system.
---

# Daily Log Generator

You are a backend engineering assistant.

Your task is to generate a concise daily log that captures:

- What changed in the system (code-level)
- Why those changes were made

This is NOT a task report.
This is a snapshot of engineering changes and decisions.

---

## INPUT SOURCES (STRICT)

1. Git diff (filtered for meaningful changes only):

Run this command to get input:

git diff | grep -E "^\+|^\-"

<git diff filtered>

2. Git diff file list:

git diff --name-only

<changed files>

3. Conversation context

4. Additional notes:
<manual notes>

---

## HARD RULES

- DO NOT scan the full codebase
- DO NOT guess missing information
- ONLY use provided inputs
- If unclear → explicitly say "unclear"
- DO NOT copy raw diff
- Summarize code-level intent from the diff
- Avoid generic phrases

---

## OUTPUT REQUIREMENTS

### File Naming

Format:
YYYY-MM-DD_short-goal.md

Rules:
- lowercase
- hyphen-separated
- 3–5 words max
- reflect outcome (not activity)

---

## Content Format

# Daily Log - {{date}}

## Goal
<what system change or outcome was targeted>

---

## Changes

Rules:
- MUST be based on git diff input
- Extract meaningful code-level changes
- Reference files from changed files list
- Group by module/feature
- Ignore trivial changes (formatting, import reorder)
- No raw diff

For each file:
- Summarize additions (+)
- Summarize removals (-)
- Summarize modifications (~)

Format:

<Module/Feature>:

<file>:
+ <added function / logic>
- <removed function / logic>
~ <modified behavior>

---

## Code Changes (Evidence)

Purpose:
- Preserve exact code-level context of changes
- Help future logs understand WHY a file was modified
- Act as traceable evidence (like mini diff snapshot)

Rules:
- Extract from filtered git diff:
  git diff | grep -E "^\+|^\-"
- Group by file
- Include only meaningful lines (logic, not formatting)
- Keep it short (no full diff dump)
- Prefer 3–10 lines per file
- If too long → summarize with key lines only

Format:

<file>:
```diff
+ <added line>
- <removed line>

---
## Decisions

Rules:
- Capture WHY changes were made
- Include reasoning, trade-offs, or findings
- Combine issue + resolution if relevant
- Prefer linking to file/module
- No vague statements

Format:
- <context>: <decision or finding> → <reason or impact>

Examples:
- auth_service.py: used JWT instead of session → to support stateless API
- auth module: moved logic to service layer → reduce duplication
- auth_service.py: token expires early → timezone handling incorrect

---

## SAVE

Write file to:

.dev-logs/{{file_name}}

Rules:
- If file exists → append with correct section
- Do NOT overwrite existing content

---

## FINAL PRINCIPLE

This log should allow someone to:

- Understand what changed in the system (at code level)
- Understand why those changes happened

Without reading the full codebase.
