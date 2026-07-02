from __future__ import annotations

import os
from typing import Any


def post_result(payload: dict[str, Any]) -> dict[str, Any]:
    import requests

    endpoint = os.getenv("SERVICENOW_ENDPOINT")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")

    if not endpoint:
        return {
            "posted": False,
            "reason": "SERVICENOW_ENDPOINT not configured. Report generated locally only.",
        }

    response = requests.post(
        endpoint,
        auth=(username, password) if username and password else None,
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return {"posted": True, "status_code": response.status_code, "response": response.text[:1000]}
