# AUDIT_LOG.md

## Reconnaissance - 20260524

### REPO_CONTEXT

| Field | Value |
|-------|-------|
| Project Name | rainbowchess |
| Language(s) | Python |
| Framework(s) | (from requirements.txt) |
| Core Purpose | Personal project |
| Test Runner | none detected |
| Dependency File | requirements.txt (15 packages) |
| Rough Complexity | Small (3 source files) |
| Existing Snyk Results | NONE |
| Snyk Scan Needed | NO |

### Phase 1 - Security Audit

SCA: 15 packages analyzed. 0 potential issues flagged.
SAST: 0 potential secret patterns detected.
Snyk: NOT NEEDED
Status: SAFE

## Portfolio upkeep task list — 2026-09-11

- [x] Restore only the two application templates removed by the earlier cleanup; preserve historical content and credits.
- [x] Reproduce undo exhaustion, mutable-piece aliasing, new-game history leakage and promotion/winner restoration.
- [x] Repair bounded undo snapshots and verify normal Flask page/move/undo flows with synthetic games.
- [ ] Publish reviewed source and report hosting evidence separately; existing shared-user state and rule gaps remain explicit.

### Verified repair — 2026-09-11

Recovered `templates/index.html` and `templates/chess.html` from the parent of cleanup commit `d8a57ab400da745accd6277a501c1b7ef04a3fc3`. Undo now owns a complete, independent game snapshot, exhausts correctly after at most ten moves, and resets for a new game. Undo restores turn, piece flags, winner and promotion state. A completed promotion clears its pending flag. The original 478 px board overflowed a 390 px viewport; its nine-column grid now fits narrow screens.

All 15 synthetic Python checks pass, including real Flask template rendering. The original source produced failures/errors for the same regression suite. Browser start/move/undo/empty-history flows pass at 1440, 390 and 320 px, with 81 board cells, no horizontal overflow and no JavaScript errors. A dedicated application workflow runs the Python checks. The local verification server was stopped afterward.

Hosting evidence: GitHub Pages is configured from `master` at `/` and reports a built static project page. There is no matching project in the recorded Vercel inventory; this source repair does not verify a production Flask runtime. Per-browser game isolation, complete rule/input validation and persistent game storage remain open. The current application keeps one game in process memory; no user records or provider settings were changed.

The first commit attempt was rejected by the local identity hook for the historical GitHub link in the copyright line. The author name and copyright remain; only that credit link is now plain text. The hook stays enabled. The home template remains byte-for-byte original; the chess template has this one intentional attribution-link change.
