from __future__ import annotations


def governance_decision(score: int, issues: list[dict[str, str]]) -> str:
    has_critical = any(issue["severity"] == "Critical" for issue in issues)
    has_high = any(issue["severity"] == "High" for issue in issues)

    if has_critical or score < 50:
        return "Block Sync"
    if has_high or score < 85:
        return "Manual Review"
    return "Allow Sync"


def should_fail_pipeline(decision: str) -> bool:
    return decision == "Block Sync"
