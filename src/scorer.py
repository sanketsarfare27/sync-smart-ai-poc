from __future__ import annotations


PENALTY_BY_SEVERITY = {
    "Critical": 100,
    "High": 35,
    "Medium": 15,
    "Low": 5,
}


def calculate_score(issues: list[dict[str, str]]) -> int:
    score = 100
    for issue in issues:
        score -= PENALTY_BY_SEVERITY.get(issue["severity"], 10)
    return max(score, 0)


def risk_level(score: int, issues: list[dict[str, str]]) -> str:
    if any(issue["severity"] == "Critical" for issue in issues) or score == 0:
        return "Critical"
    if score < 70:
        return "High"
    if score < 90:
        return "Medium"
    return "Low"
