def generate_ai_summary(update_set, issues, score, decision):
    """
    Day 1 placeholder.
    Day 2 मध्ये इथे OpenAI / Azure OpenAI integration add करू.
    """

    if not issues:
        return "No major risk found. Update set appears safe for GitHub sync."

    critical_count = len([i for i in issues if i.get("severity") == "Critical"])
    high_count = len([i for i in issues if i.get("severity") == "High"])
    medium_count = len([i for i in issues if i.get("severity") == "Medium"])
    low_count = len([i for i in issues if i.get("severity") == "Low"])

    return (
        f"Validation found {len(issues)} issue(s): "
        f"{critical_count} Critical, {high_count} High, "
        f"{medium_count} Medium, {low_count} Low. "
        f"Final decision is {decision} with confidence score {score}/100."
    )