from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from ai_reviewer import review_risk
from check_gate import governance_decision, should_fail_pipeline
from parser import parse_update_set
from post_to_servicenow import post_result
from rule_validator import load_baseline, validate_rules
from scorer import calculate_score, risk_level


def build_payload(update_set_path: Path, baseline_path: Path) -> dict[str, Any]:
    parsed = parse_update_set(update_set_path)
    baseline = load_baseline(baseline_path)
    issues = validate_rules(parsed, baseline)
    score = calculate_score(issues)
    decision = governance_decision(score, issues)
    ai_review = review_risk(parsed.update_set_name, issues)

    return {
        "update_set_name": parsed.update_set_name,
        "file_name": parsed.file_name,
        "score": score,
        "confidence_score": score,
        "decision": decision,
        "risk_level": risk_level(score, issues),
        "review_status": "Received",
        "issues": issues,
        "issues_json": json.dumps(issues, indent=2),
        **ai_review,
        "github_repo": os.getenv("GITHUB_REPOSITORY", "sanketsarfare27/sync-smart-ai-poc"),
        "github_run_url": os.getenv("GITHUB_RUN_URL", "GitHub Action run URL"),
        "branch": os.getenv("GITHUB_REF_NAME", "main"),
        "commit_sha": os.getenv("GITHUB_SHA", "commit id"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ServiceNow update set before sync.")
    parser.add_argument("--update-set", required=True, help="Path to update set XML")
    parser.add_argument("--baseline", default="baseline/existing_objects.json", help="Path to baseline JSON")
    parser.add_argument("--report-dir", default="reports", help="Folder where JSON reports are written")
    parser.add_argument("--post-servicenow", action="store_true", help="POST result to ServiceNow endpoint")
    args = parser.parse_args()

    update_set_path = Path(args.update_set)
    baseline_path = Path(args.baseline)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(update_set_path, baseline_path)
    report_path = report_dir / f"{update_set_path.stem}_report.json"
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"Report written: {report_path}")

    if args.post_servicenow:
        post_status = post_result(payload)
        print(json.dumps(post_status, indent=2))

    return 1 if should_fail_pipeline(payload["decision"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
