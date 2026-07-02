from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from parser import ParsedUpdateSet, UpdateSetObject


SECRET_PATTERNS = [
    re.compile(r"sk_live_[A-Za-z0-9_=-]{8,}", re.IGNORECASE),
    re.compile(r"(password|passwd|token|secret|api[_-]?key)\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
]


def _issue(severity: str, issue: str, recommendation: str, obj: UpdateSetObject | None = None) -> dict[str, str]:
    result = {
        "severity": severity,
        "issue": issue,
        "recommendation": recommendation,
    }
    if obj:
        result["object"] = obj.name
        result["object_type"] = obj.object_type
        result["sys_id"] = obj.sys_id
    return result


def load_baseline(path: str | Path) -> dict[str, Any]:
    baseline_path = Path(path)
    return json.loads(baseline_path.read_text(encoding="utf-8"))


def validate_rules(update_set: ParsedUpdateSet, baseline: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    baseline_ids = {obj["sys_id"] for obj in baseline.get("objects", [])}
    baseline_names = {(obj["type"], obj["name"]) for obj in baseline.get("objects", [])}

    if not update_set.objects:
        issues.append(
            _issue(
                "High",
                "Update set does not contain deployable objects",
                "Verify the exported update set file before sync.",
            )
        )

    for obj in update_set.objects:
        if obj.sys_id in baseline_ids or (obj.object_type, obj.name) in baseline_names:
            issues.append(
                _issue(
                    "High",
                    "Object conflict found against baseline",
                    "Review the existing object owner and confirm overwrite or merge strategy.",
                    obj,
                )
            )

        if any(pattern.search(obj.script) for pattern in SECRET_PATTERNS):
            issues.append(
                _issue(
                    "Critical",
                    "Hardcoded token found",
                    "Move token to a secure credential store and rotate the exposed value.",
                    obj,
                )
            )

        if "deleteMultiple()" in obj.script or ".deleteRecord()" in obj.script:
            issues.append(
                _issue(
                    "Critical",
                    "Bulk delete or record delete logic found",
                    "Require manual architecture review and add rollback evidence before deployment.",
                    obj,
                )
            )

        if obj.object_type == "sys_script" and not obj.condition:
            issues.append(
                _issue(
                    "Medium",
                    "Business rule condition is empty",
                    "Add a precise condition to reduce unintended execution.",
                    obj,
                )
            )

        if obj.table in {"sys_user", "sys_user_has_role", "sys_security_acl"}:
            issues.append(
                _issue(
                    "High",
                    f"Sensitive table change detected: {obj.table}",
                    "Route to platform security owner for approval before sync.",
                    obj,
                )
            )

    return issues
