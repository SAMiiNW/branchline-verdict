# Branchline Verdict

Branchline Verdict turns a published binary decision tree into an inspectable route. Validators read one complete public case record, answer the tree's questions in order, and return the exact question indexes they followed. The contract—not the language model—derives the terminal outcome from that route.

## Route legend

- `Q:n` continues to question `n`.
- `OUT:LABEL` ends at a declared outcome.
- Every branch must move forward, every question must be reachable, and cycles are rejected when the tree is opened.
- A case cannot skip a question, invent an index, continue after a terminal branch, or stop before reaching one.

## On-chain journey

1. `open_tree` freezes the questions, branch targets, and outcomes.
2. `file_case` records a case ID, tree ID, label, and HTTPS source.
3. `walk_case` fetches the complete record under a 12,000-byte cap and asks validators for only the ordered path.
4. The contract replays the path and stores the derived outcome plus the full-source SHA-256 digest.
5. `get_case` exposes the route, outcome, source digest, sender, and state.

## Run the checks

```powershell
genvm-lint contracts\contract.py
pytest -q tests
```

The live StudioNet deployment and transaction proof are written to `deployment.json` and `evidence/live-run.json` by the scripts in `scripts/`.

## Review fixture

`fixtures/case-clear.md` is an operator-controlled case record used only to demonstrate the route protocol. It is not presented as independent production data.
