def calculate_score_and_decision(issues):
    """
    Calculates confidence score based on issue severity.
    """

    penalty_map = {
        "Critical": 45,
        "High": 25,
        "Medium": 15,
        "Low": 5
    }

    score = 100

    for issue in issues:
        severity = issue.get("severity", "Low")
        score -= penalty_map.get(severity, 5)

    score = max(score, 0)

    if score >= 80:
        decision = "Allow Sync"
    elif score >= 60:
        decision = "Manual Review"
    else:
        decision = "Block Sync"

    return score, decision