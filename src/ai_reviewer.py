from __future__ import annotations


def review_risk(update_set_name: str, issues: list[dict[str, str]]) -> dict[str, str]:
    """AI reviewer boundary: explain risk and suggest fixes, never decide release outcome."""
    if not issues:
        return {
            "ai_summary": f"{update_set_name} appears low risk based on the current rule scan.",
            "ai_risk_summary": "No material security, conflict, or deployment risk was detected by the hard validation layer.",
            "ai_business_impact": "Expected business impact is low because the update set does not touch sensitive tables or destructive logic.",
            "ai_suggested_fixes": "Proceed with normal peer review and retain deployment evidence.",
            "ai_final_recommendation": "AI reviewer suggests no additional remediation. Final decision must still come from the governance gate.",
        }

    severities = [item["severity"] for item in issues]
    critical_count = severities.count("Critical")
    high_count = severities.count("High")
    top_issues = "; ".join(item["issue"] for item in issues[:3])

    if critical_count:
        risk_summary = "Critical risk exists because the update set includes security-sensitive or destructive patterns."
        business_impact = "Deployment could expose secrets, delete data, or create audit and operational incidents."
    elif high_count:
        risk_summary = "High risk exists because the update set collides with baseline objects or touches sensitive platform areas."
        business_impact = "Deployment may overwrite existing configuration or require additional owner approval."
    else:
        risk_summary = "Moderate risk exists because some implementation controls are incomplete."
        business_impact = "Deployment can proceed only after targeted cleanup and reviewer confirmation."

    fixes = " | ".join(item["recommendation"] for item in issues[:4])

    return {
        "ai_summary": f"{update_set_name} has {len(issues)} flagged issue(s): {top_issues}.",
        "ai_risk_summary": risk_summary,
        "ai_business_impact": business_impact,
        "ai_suggested_fixes": fixes,
        "ai_final_recommendation": "AI reviewer provides explanation only. Governance gate must make the final Allow, Manual Review, or Block decision.",
    }
