# Persistent project records

## Contents

1. PROJECT_STATE
2. PROJECT_LOG
3. ADRs
4. Evidence and validation
5. Lessons promotion

## 1. PROJECT_STATE

Keep `docs/PROJECT_STATE.md` short and current. It must answer:

- What is the project and active hardware revision?
- Which schematic/PCB/variant is authoritative?
- What phase is active?
- What was last validated?
- What blocks progress?
- What are the next three actions?

Rewrite this file as state changes; it is a handoff, not history.

## 2. PROJECT_LOG

Keep `docs/PROJECT_LOG.md` append-only. For each meaningful event record:

- timestamp and event type;
- summary and reason;
- files/components/nets affected;
- sources and assumptions;
- validation performed and result;
- open risks and next action;
- related commit or issue when available.

Use `tools/pcb_design/record_event.py` to keep formatting consistent. For an
older project without local tools, use the matching script from the installed
skill.

## 3. ADRs

Name decisions `ADR-0001-short-title.md`. Include:

- Status: proposed, accepted, superseded, rejected.
- Context.
- Options considered.
- Decision and reasons.
- Consequences and risks.
- Sources/evidence.
- Required validation.

Do not edit an accepted ADR to hide a former decision. Add a superseding ADR.

## 4. Evidence and validation

Store immutable snapshots below `docs/validation/YYYYMMDD-HHMM-label/`:

- Git revision and dirty status;
- SHA-256 hashes of KiCad sources;
- ERC/DRC reports;
- BOM/CPL validation;
- measurements, photos, and test conditions.

Use `tools/pcb_design/snapshot_project.py` before milestones and production
handoffs. For an older project without local tools, use the matching script from
the installed skill.

The snapshot tool copies `build/pcb-design-check/` automatically when present.
Do not call a snapshot release evidence when no applicable reports were copied.

## 5. Lessons promotion

Record project-specific lessons in `docs/LESSONS.md`. Promote a lesson to the
central system when:

- it occurs in more than one project;
- it prevents a high-impact failure;
- it can become a deterministic check;
- it changes the standard design/release procedure.
