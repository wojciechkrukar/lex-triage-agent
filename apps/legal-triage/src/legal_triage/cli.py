"""CLI entry point for the legal triage app."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Legal Email Triage Pipeline")
    parser.add_argument("--export-mermaid", action="store_true", help="Print Mermaid graph diagram")
    parser.add_argument("--email-file", type=Path, help="Path to email JSON file to process")
    args = parser.parse_args()

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
