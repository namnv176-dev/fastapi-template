# PROJECT.md — Project Context

> This file captures project-specific business context, domain rules, and feature scope.
> It is **per-project** and not reusable across templates.
> AI agents should read this file alongside `AGENTS.md` before starting any task.

---

## Project Identity

| Field | Value |
|-------|-------|
| **Name** | [Fill in: project name] |
| **Domain** | [Fill in: e.g., E-commerce / SaaS / Internal Tool / AI API] |
| **Stage** | [Fill in: MVP / Beta / Production / Maintenance] |
| **Primary Audience** | [Fill in: e.g., end users / internal teams / third-party developers] |

---

## Business Goals

> List the core problems this project solves and what success looks like.

1. [Fill in: Goal 1]
2. [Fill in: Goal 2]
3. [Fill in: Goal 3]

---

## Domain Modules

> Keep this table updated as new modules are added or responsibilities shift.

| Module | Responsibility | Status |
|--------|---------------|--------|
| `user` | Authentication, profile management | [Stable / In Dev / Planned] |
| [module] | [responsibility] | [status] |

---

## Business Rules

> Domain constraints that must be enforced at all times. These are non-negotiable invariants.

- [Fill in: e.g., "User email must be unique across the system"]
- [Fill in: e.g., "An order cannot be cancelled after it has been shipped"]
- [Fill in: e.g., "Only admins can perform hard deletes"]

---

## External Integrations

> Services this project communicates with and where credentials are stored.

| Service | Purpose | Credential Key in `.env` |
|---------|---------|--------------------------|
| [Fill in: e.g., Stripe] | [Fill in: e.g., Payment processing] | [Fill in: e.g., `STRIPE_SECRET_KEY`] |

---

## Non-Goals

> Explicitly state what this project does NOT do to prevent scope creep.

- [Fill in: e.g., "No real-time features (WebSocket)"]
- [Fill in: e.g., "No multi-tenancy support"]
- [Fill in: e.g., "No mobile application"]
