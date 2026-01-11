# TASKS.md — Pyodide Ship Combat Project

> Authoritative task ledger + memory anchor for systematic PR improvement work on pyodide-ship-combat.
> Rule: Only pick next batch from unchecked tasks [ ]. Add new work here first (ANTI-DRIFT).

---

## 0) Run Protocol (mandatory every run)

- [x] Read TASKS.md fully and pick next batch ONLY from unchecked tasks.
- [x] Confirm this run's batch + exit criteria are explicitly listed under "1) Current Batch".
- [ ] End of run: update TASKS.md + STATUS.md + PR_INVENTORY.md, produce artifact, output link + changelog + next plan.

---

## 1) Current Batch (choose ONE batch at a time)

### Batch ID: BATCH-002 🔄 IN PROGRESS

**Batch Type**: Documentation Audit & Improvement

**Exit Criteria for this batch:**

- [ ] All existing .md files reviewed and updated
- [ ] Documentation gaps identified and documented
- [ ] CONTRIBUTING.md created with PR guidelines
- [ ] Test running procedures documented
- [ ] Known limitations documented
- [ ] TASKS.md updated with completion status
- [ ] STATUS.md updated with findings
- [ ] CHANGELOG.md updated with Batch-002 entry

**Previous Batch:** BATCH-001 ✅ COMPLETED (Infrastructure Setup)

---

## 2) Coverage Strategy

- [x] Define scope: Work on open PRs and improvement items without merge conflicts
- [x] Enumerate all open PRs requiring review/action
  - PR #27 (WIP): Documentation improvements (current branch)
  - PR #20: Add e2e test suite
  - PR #19: Make phase snapshots JSON-serializable
  - PR #18: Freeze battle snapshots
  - PR #15: Remove redundant heading arrow logic
  - PR #14: Fix damage tracking and namespace pollution
  - PR #13: Fix misleading health calculation
  - PR #12: Remove redundant condition checks
  - PR #11: Remove redundant lower-bound checks
- [x] Create PR_INVENTORY.md with status tracking
- [ ] Document items excluded from processing and rationale
- [x] Add "Coverage Strategy" section to STATUS.md

---

## 3) Deliverables (top-down order)

### Core Tracking Files

- [x] Create TASKS.md (this file)
- [x] Create STATUS.md with current state
- [x] Create PR_INVENTORY.md with status tags
- [x] Create CHANGELOG.md documenting milestones

### Documentation Improvements (PR #27 Focus)

- [x] Review and improve project documentation structure
  - [x] Verify README.md completeness and clarity (reviewed - comprehensive)
  - [x] Check AGENTS.md alignment with current practices (reviewed - accurate)
  - [x] Validate DESIGN_CANVAS.md accuracy (reviewed - up to date)
  - [ ] Review ADVANCED_FEATURES.md coverage
  - [ ] Ensure LOGGING.md is comprehensive
  - [ ] Review SHIP_BUILDING.md completeness
- [x] Create systematic documentation tracking
  - [x] Document gaps in current documentation
  - [x] Prioritize documentation improvements
  - [x] Define documentation standards in CONTRIBUTING.md

### Code Quality Improvements (PRs #11-15)

- [ ] Review redundant condition fixes (PRs #11, #12, #15)
  - [ ] Analyze changes for correctness
  - [ ] Verify no behavioral changes
  - [ ] Check test coverage
- [ ] Review health calculation fix (PR #13)
  - [ ] Validate calculation accuracy
  - [ ] Check display formatting
- [ ] Review damage tracking fix (PR #14)
  - [ ] Verify statistics tracking completeness
  - [ ] Check namespace pollution fixes
  - [ ] Validate __all__ exports

### Feature Enhancements (PRs #18-20)

- [ ] Review snapshot freezing (PR #18)
  - [ ] Verify immutability implementation
  - [ ] Check test coverage
- [ ] Review JSON serialization (PR #19)
  - [ ] Validate FrozenDict approach
  - [ ] Check compatibility with UI layers
- [ ] Review e2e test suite (PR #20)
  - [ ] Verify test coverage
  - [ ] Check deterministic stubbing
  - [ ] Validate documentation updates

### Configuration/Setup

- [ ] Document how to run tests for each PR
- [ ] Set up validation workflow
- [ ] Create merge conflict detection strategy
- [ ] Document PR review process

### Documentation Category

- [x] Create CONTRIBUTING.md with PR guidelines
- [x] Create PR template (.github/PULL_REQUEST_TEMPLATE.md)
- [x] Create TESTING.md with comprehensive test guide
- [ ] Document branching strategy (added to CONTRIBUTING.md)
- [ ] Document known limitations and edge cases

### Quality/Testing

- [x] Run existing test suite to establish baseline
- [x] Identify any broken tests (not related to PRs)
- [x] Document test running procedures (TESTING.md created)
- [ ] Document coverage gaps

---

## 4) Quality Gates (repeat regularly)

### PR Compatibility Audit

- [ ] Check each batch for merge conflicts with open PRs
- [ ] Verify changes don't duplicate PR work
- [ ] Ensure documentation changes are orthogonal to PR changes
- [ ] Validate no breaking changes to PR branches

### Documentation Quality

- [ ] Verify all documentation is accurate and current
- [ ] Check for broken links in markdown files
- [ ] Ensure code examples are valid
- [ ] Validate documentation follows project style

### Code Quality (when touching code)

- [ ] Run linters on modified files
- [ ] Run tests affected by changes
- [ ] Verify Pyodide compatibility
- [ ] Check browser compatibility for changes

---

## 5) Cleanup & Maintenance

- [ ] Remove temporary tracking files not needed long-term
  - [ ] Evaluate if TASKS.md should remain after project completion
  - [ ] Evaluate if STATUS.md should remain after project completion
  - [ ] Evaluate if CHANGELOG.md should be archived
- [ ] Archive or reorganize deliverables
- [ ] Clean up workspace
- [ ] Verify .gitignore covers generated files

---

## 6) Version Control & Release

- [ ] Review all staged changes for commit
  - [ ] Tracking files (TASKS.md, STATUS.md, etc.)
  - [ ] Documentation improvements
  - [ ] Any code changes
- [ ] Create detailed commit message documenting:
  - [ ] Infrastructure setup
  - [ ] Documentation improvements
  - [ ] PR compatibility notes
- [ ] Push staged changes to remote
- [ ] Update PR #27 description with progress

---

## 7) Future Work (After Batch Completion)

- [ ] Consolidate similar PRs (e.g., PRs #11-15 all fix similar issues)
- [ ] Create comprehensive PR for code quality fixes
- [ ] Support review and merging of feature PRs (#18-20)
- [ ] Create documentation improvement PR
- [ ] Set up automated testing for future PRs
- [ ] Create PR checklist template

---

## 8) Packaging & Delivery (every run)

- [ ] Update STATUS.md with batch completion status
- [ ] Update PR_INVENTORY.md tags ([TODO]/[IN_PROGRESS]/[COMPLETED])
- [ ] Produce artifact: Complete tracking file set
- [ ] Output: artifact link + changelog + next execution plan

---

## 9) Known Blockers & Dependencies

- [ ] Need to verify test infrastructure works correctly
- [ ] Need to understand merge strategy for multiple similar PRs
- [ ] Need to confirm documentation scope for PR #27
- [ ] Need to validate Pyodide compatibility for any code changes

---

## 10) Next Immediate Actions (Priority Order)

- [x] Create all tracking files (TASKS.md, STATUS.md, PR_INVENTORY.md, CHANGELOG.md)
- [ ] Complete PR analysis and populate PR_INVENTORY.md with details
- [ ] Run existing test suite to establish baseline
- [ ] Review documentation files for gaps and improvements
- [ ] Define Batch-002: Documentation improvements
- [ ] Execute Batch-002 work
- [ ] Update tracking files with progress
- [ ] Report progress and plan next batch

---

## Usage Notes

This TASKS.md follows the PROJECT-AGNOSTIC AGENT INSTRUCTIONS template for systematic, verifiable, batched task execution with durable progress tracking. All work is organized into batches with explicit exit criteria, and progress is tracked through companion files (STATUS.md, PR_INVENTORY.md, CHANGELOG.md).

Key principles:
- **ANTI-DRIFT**: Add tasks here BEFORE doing work not already listed
- **Batch execution**: Pick ONE batch at a time with clear exit criteria
- **Truth in tracking**: Mark complete only when verified
- **Durable artifacts**: Always produce tracking files and deliverables
- **Interruption-safe**: Can pause/resume at any batch boundary
