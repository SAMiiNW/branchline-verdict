import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from genlayer_py.contracts import actions as contract_actions


def calldata_compat(method=None, args=None, kwargs=None):
    result = {}
    if method is not None:
        result["method"] = method
    if args:
        result["args"] = args
    if kwargs:
        result["kwargs"] = kwargs
    return result


contract_actions.make_calldata_object = calldata_compat
ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / "accounts.env").read_text(encoding="utf-8")
KEY = re.search(r'^ACCOUNT_1_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M).group(1).strip()
client = create_client(chain=studionet, account=create_account(account_private_key=KEY))
address = json.loads((ROOT / "deployment.json").read_text(encoding="utf-8"))["contractAddress"]


def finalized(name, args, expected="SUCCESS"):
    tx = client.write_contract(address=address, function_name=name, args=args)
    print(name + "_tx=" + str(tx), flush=True)
    receipt = client.wait_for_transaction_receipt(transaction_hash=tx, wait_until="finalized", retries=180, interval=5000, full_transaction=True)
    leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
    assert receipt.get("result_name") == "MAJORITY_AGREE" and leader.get("execution_result") == expected, receipt
    return str(tx), leader


stamp = str(int(time.time()))
tree_id = "ROUTE-" + stamp
case_id = "CASE-" + stamp
questions = [
    "Does the published case state that the notice arrived before the 17:00 UTC cutoff?",
    "Does the published case confirm that the shipment carries valid transit insurance?",
    "Does the published case disclose any unresolved ownership conflict?",
]
yes_targets = ["Q:1", "Q:2", "OUT:REVIEW"]
no_targets = ["OUT:LATE", "OUT:INCOMPLETE", "OUT:CLEAR"]
outcomes = ["CLEAR", "LATE", "INCOMPLETE", "REVIEW"]
source = "https://cdn.jsdelivr.net/gh/SAMiiNW/branchline-verdict@main/fixtures/case-clear.md"

open_tx, _ = finalized("open_tree", [tree_id, "Harbor release routing tree", questions, yes_targets, no_targets, outcomes])
file_tx, _ = finalized("file_case", [case_id, tree_id, "Atlas manifest release", source])
before = client.read_contract(address=address, function_name="get_case", args=[case_id])
duplicate_tx, duplicate_leader = finalized("file_case", [case_id, tree_id, "Duplicate should fail", source], expected="ERROR")
after_rejection = client.read_contract(address=address, function_name="get_case", args=[case_id])
assert before == after_rejection and before["state"] == "FILED"
walk_tx, _ = finalized("walk_case", [case_id])
record = client.read_contract(address=address, function_name="get_case", args=[case_id])
assert record["state"] == "ROUTED" and record["outcome"] == "CLEAR", record
assert [step["question"] for step in record["path"]] == [0, 1, 2], record
proof = {
    "treeId": tree_id,
    "caseId": case_id,
    "transactions": {"openTree": open_tx, "fileCase": file_tx, "duplicateRejected": duplicate_tx, "walkCase": walk_tx},
    "negativeExecution": duplicate_leader.get("execution_result"),
    "stateUnchangedAfterRejectedDuplicate": before == after_rejection,
    "finalCase": record,
    "fixtureDisclosure": "The public case page is an operator-controlled fixture used to prove deterministic root-to-terminal routing.",
}
(ROOT / "evidence").mkdir(exist_ok=True)
(ROOT / "evidence" / "live-run.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
print(json.dumps(proof, indent=2), flush=True)
