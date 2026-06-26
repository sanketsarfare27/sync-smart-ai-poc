import json
import re
from pathlib import Path


SECRET_PATTERNS = [
    ("Hardcoded password found", re.compile(r"password\s*=\s*['\"].+?['\"]", re.IGNORECASE)),
    ("Hardcoded token found", re.compile(r"token\s*=\s*['\"].+?['\"]", re.IGNORECASE)),
    ("Hardcoded API key found", re.compile(r"api[_-]?key\s*=\s*['\"].+?['\"]", re.IGNORECASE)),
]

RISKY_PATTERNS = [
    ("current.update() used in script", re.compile(r"current\.update\s*\(", re.IGNORECASE)),
    ("gs.log() used in script", re.compile(r"gs\.log\s*\(", re.IGNORECASE)),
]


def load_baseline(baseline_path):
    baseline_path = Path(baseline_path)

    if not baseline_path.exists():
        return {"objects": []}

    with open(baseline_path, "r", encoding="utf-8") as file:
        return json.load(file)


def add_issue(issues, severity, issue, object_name, object_type, recommendation):
    issues.append({
        "severity": severity,
        "issue": issue,
        "object_name": object_name,
        "object_type": object_type,
        "recommendation": recommendation
    })


def validate_update_set(update_set, baseline):
    """
    Performs basic Day 1 rule checks:
    1. Duplicate sys_id conflict
    2. Hardcoded password/token/API key
    3. current.update()
    4. Missing dependency
    5. Basic naming warning
    """

    issues = []

    baseline_objects = baseline.get("objects", [])

    baseline_sys_ids = {
        obj.get("sys_id"): obj
        for obj in baseline_objects
        if obj.get("sys_id")
    }

    baseline_names = {
        obj.get("name")
        for obj in baseline_objects
        if obj.get("name")
    }

    current_update_set_names = {
        obj.get("name")
        for obj in update_set.get("objects", [])
        if obj.get("name")
    }

    available_names = baseline_names.union(current_update_set_names)

    for obj in update_set.get("objects", []):
        object_type = obj.get("type", "")
        object_name = obj.get("name", "")
        sys_id = obj.get("sys_id", "")
        script = obj.get("script", "") or ""
        dependencies = obj.get("dependencies", [])

        # Rule 1: sys_id conflict
        if sys_id in baseline_sys_ids:
            add_issue(
                issues,
                "Critical",
                f"Conflict detected: sys_id {sys_id} already exists in GitHub baseline",
                object_name,
                object_type,
                "Review existing GitHub object before syncing this update set."
            )

        # Rule 2: Naming standard warning
        if len(object_name) < 5:
            add_issue(
                issues,
                "Low",
                "Object name is too short or unclear",
                object_name,
                object_type,
                "Use a clear naming convention for ServiceNow objects."
            )

        # Rule 3: Secret patterns
        for issue_text, pattern in SECRET_PATTERNS:
            if pattern.search(script):
                add_issue(
                    issues,
                    "Critical",
                    issue_text,
                    object_name,
                    object_type,
                    "Move secrets to secure credential store or system properties."
                )

        # Rule 4: Risky patterns
        for issue_text, pattern in RISKY_PATTERNS:
            if pattern.search(script):
                severity = "High" if "current.update" in issue_text else "Medium"
                add_issue(
                    issues,
                    severity,
                    issue_text,
                    object_name,
                    object_type,
                    "Review script logic. Avoid risky operations before deployment."
                )

        # Rule 5: Missing dependency
        for dependency in dependencies:
            if dependency not in available_names:
                add_issue(
                    issues,
                    "Medium",
                    f"Missing dependency: {dependency}",
                    object_name,
                    object_type,
                    "Include missing dependency in the update set or confirm it exists in target environment."
                )

    return issues