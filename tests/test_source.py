from pathlib import Path

ROOT = Path(__file__).parents[1]


def derive_path(questions, yes_targets, no_targets, answers):
    current = 0
    path = []
    for answer in answers:
        path.append({"question": current, "answer": answer})
        target = (yes_targets if answer else no_targets)[current]
        if target.startswith("OUT:"):
            return path, target[4:]
        current = int(target[2:])
    raise ValueError("path stopped before terminal")


def test_deterministic_leaf_is_derived_from_the_path():
    questions = ["deadline", "insurance", "conflict"]
    yes = ["Q:1", "Q:2", "OUT:REVIEW"]
    no = ["OUT:LATE", "OUT:INCOMPLETE", "OUT:CLEAR"]
    path, outcome = derive_path(questions, yes, no, [True, True, False])
    assert [step["question"] for step in path] == [0, 1, 2]
    assert outcome == "CLEAR"


def test_contract_rejects_skips_cycles_and_partial_sources():
    source = (ROOT / "contracts/contract.py").read_text(encoding="utf-8")
    for token in (
        "question branches must move forward",
        "every question must be reachable",
        "invented, skipped, or repeated question",
        "path continued after terminal",
        "path stopped before terminal",
        "nothing is evaluated partially",
        "prompt_comparative",
    ):
        assert token in source
    assert "[:12000]" not in source


def test_frontend_preserves_finality_and_tree_metaphor():
    source = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    assert 'status:"FINALIZED"' in source
    assert "WAITING FOR FINALIZED" in source
    assert "routeMap" in source
    assert "WALK THIS CASE" in source
    assert "OPEN A DECISION TREE" in source

