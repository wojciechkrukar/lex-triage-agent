"""
Smoke-test the interactive pipeline: load emails, run the two-stage HITL
logic in auto mode with tier3 stubs, verify routing and queue tracking.
"""
import os, sys, json
from pathlib import Path
from collections import Counter

os.environ["LLM_TIER"] = "tier3"
os.environ["LANGSMITH_TRACING"] = "false"

REPO = Path(__file__).parent
sys.path.insert(0, str(REPO / "apps/legal-triage/src"))

from legal_triage.graph import get_compiled_graph
from legal_triage.state import initial_state
from legal_triage.nodes.router import router_node
import legal_triage.hitl_queue as hitl_queue

GRAPH = get_compiled_graph()

CLASS_TO_SINK = {
    "pi_lead": "NewLead", "general_legal": "GeneralLegal",
    "spam": "Refused-Spam", "invoice": "Refused-Invoice", "other": "Refused-Other",
}


def strip_gt(r):
    return {k: v for k, v in r.items() if not k.startswith("gt_")}


records = []
path = REPO / "apps/dataset-generator/out/emails_gt.jsonl"
with path.open() as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))
        if len(records) >= 20:
            break

print(f"Loaded {len(records)} emails")

hitl_queue.reset()
results = []
for i, rec in enumerate(records):
    gt_class = rec.get("gt_class", "other")
    pub = strip_gt(rec)
    state = initial_state(
        email_id=pub.get("email_id", f"smk-{i:04d}"),
        raw_email=pub.get("body", ""),
        attachments=pub.get("attachments", []),
    )
    result = dict(GRAPH.invoke(state))

    if result.get("hitl_required") and result.get("human_decision") is None:
        score = result.get("appraisal_score") or 0.5
        decision = "approve" if score >= 0.5 else "reject"
        result["human_decision"] = decision
        result.update(router_node(result))
        hitl_queue.dequeue()

    results.append({
        "gt_class": gt_class,
        "terminal_sink": result.get("terminal_sink"),
        "expected_sink": CLASS_TO_SINK.get(gt_class, "Refused-Other"),
        "hitl_required": result.get("hitl_required"),
        "human_decision": result.get("human_decision"),
        "hitl_queue_depth": result.get("hitl_queue_depth", 0),
    })

sinks = Counter(r["terminal_sink"] for r in results)
hitl_count = sum(1 for r in results if r["hitl_required"])
correct = sum(1 for r in results if r["terminal_sink"] == r["expected_sink"])
print(f"Routing           : {dict(sinks)}")
print(f"HITL triggered    : {hitl_count}/{len(results)}")
print(f"Correct routing   : {correct}/{len(results)} ({correct/len(results):.0%})")
print(f"Final queue depth : {hitl_queue.depth()}")
print(f"Queue depths seen : {sorted(set(r['hitl_queue_depth'] for r in results))}")
assert all(r["terminal_sink"] is not None for r in results), "Some emails have no terminal_sink!"
assert hitl_queue.depth() == 0, f"Queue not empty: {hitl_queue.depth()}"
print("✅ Smoke test PASSED")
