"""CLI entry point for the legal triage app."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Legal Email Triage Pipeline")
    subparsers = parser.add_subparsers(dest="command")

    # ------------------------------------------------------------------
    # legacy / top-level flags (kept for backwards compat)
    # ------------------------------------------------------------------
    parser.add_argument("--export-mermaid", action="store_true", help="Print Mermaid graph diagram")
    parser.add_argument("--email-file", type=Path, help="Path to email JSON file to process")

    # ------------------------------------------------------------------
    # eval subcommand
    # ------------------------------------------------------------------
    eval_parser = subparsers.add_parser("eval", help="Run evaluation harness against a ground-truth dataset")
    eval_parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Path to ground-truth JSONL file (e.g. apps/dataset-generator/out/emails_demo_gt.jsonl)",
    )
    eval_parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        metavar="N",
        help="Limit evaluation to the first N records",
    )
    eval_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for benchmark JSON outputs (default: runtime/benchmarks/)",
    )
    eval_parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="Overwrite runtime/benchmarks/baseline.json with this run's results",
    )
    eval_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-record results to stdout",
    )

    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------
    if args.command == "eval":
        from legal_triage.eval import run_eval

        report = run_eval(
            dataset_path=args.dataset,
            max_records=args.max_records,
            output_dir=args.output_dir,
            save_baseline=args.save_baseline,
            verbose=args.verbose,
        )
        kpis = report["kpis"]
        print(
            f"\nEval run: {report['run_id']}\n"
            f"  Records:           {kpis['n_records']}\n"
            f"  Lead Precision:    {kpis['lead_precision']:.3f}\n"
            f"  Lead Recall:       {kpis['lead_recall']:.3f}\n"
            f"  Spam FPR:          {kpis['spam_fpr']:.3f}\n"
            f"  Accuracy:          {kpis['accuracy']:.3f}\n"
            f"  Mean latency (ms): {kpis['mean_latency_ms']:.0f}\n"
            f"  P90 latency (ms):  {kpis['p90_latency_ms']:.0f}\n"
            f"  Total cost (USD):  {kpis['total_cost_usd']:.4f}\n"
            f"  Errors:            {kpis['n_errors']}\n"
            f"  Saved to:          {args.output_dir or 'runtime/benchmarks/'}"
        )
        return

    if args.export_mermaid:
        from legal_triage.graph import export_mermaid

        print(export_mermaid())
        return

    if args.email_file:
        from legal_triage.graph import get_compiled_graph
        from legal_triage.state import initial_state

        email_data = json.loads(args.email_file.read_text())
        state = initial_state(
            email_id=email_data.get("email_id", "cli-001"),
            raw_email=email_data.get("body", ""),
            attachments=email_data.get("attachments", []),
        )
        graph = get_compiled_graph()
        result = graph.invoke(state)
        print(json.dumps(result, indent=2, default=str))
        return

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
