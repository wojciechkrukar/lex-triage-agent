"""CLI entry point for the dataset generator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dataset_generator.config import DataGenConfig
from dataset_generator.generator import generate_public_emails, generate_raw_emails
from dataset_generator.chokepoint import assert_no_gt_fields


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic legal email dataset")
    parser.add_argument("--out", type=Path, default=Path("apps/dataset-generator/out/emails.jsonl"))
    parser.add_argument("--count", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--with-gt", action="store_true", help="Include ground-truth labels (for eval harness only)")
    parser.add_argument(
        "--realistic-split",
        action="store_true",
        help="Use 30%% PI / 70%% noise distribution (demo mode). "
             "Default is 60%% PI (M1 exit-criteria mode).",
    )
    args = parser.parse_args()

    cfg = DataGenConfig()
    count = args.count or cfg.dataset_count
    seed = args.seed or cfg.random_seed

    args.out.parent.mkdir(parents=True, exist_ok=True)

    if args.with_gt:
        records = generate_raw_emails(count, seed, args.realistic_split)
        print(f"WARNING: Writing {count} emails WITH ground-truth labels to {args.out}", file=sys.stderr)
    else:
        records = generate_public_emails(count, seed, args.realistic_split)
        # Invariant: verify no GT fields leaked
        for r in records:
            assert_no_gt_fields(r)

    with args.out.open("w") as f:
        for r in records:
            f.write(r.model_dump_json() + "\n")

    print(f"Generated {count} emails -> {args.out}")


if __name__ == "__main__":
    main()
