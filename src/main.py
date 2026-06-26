from pathlib import Path
import json
import html

from parser import parse_update_set
from rule_validator import load_baseline, validate_update_set
from scorer import calculate_score_and_decision
from ai_reviewer import generate_ai_summary


ROOT_DIR = Path(__file__).resolve().parents[1]
UPDATE_SET_DIR = ROOT_DIR / "update_sets"
BASELINE_FILE = ROOT_DIR / "baseline" / "existing_objects.json"
REPORTS_DIR = ROOT_DIR / "reports"


def build_html_report(results):
    rows = ""

    for result in results:
        issue_items = ""

        if result["issues"]:
            for issue in result["issues"]:
                issue_items += f"""
                <li>
                    <b>{html.escape(issue['severity'])}</b> - 
                    {html.escape(issue['issue'])}
                    <br/>
                    <small>
                        Object: {html.escape(issue['object_type'])} - {html.escape(issue['object_name'])}
                    </small>
                    <br/>
                    <small>
                        Recommendation: {html.escape(issue['recommendation'])}
                    </small>
                </li>
                """
        else:
            issue_items = "<li>No issues found</li>"

        rows += f"""
        <tr>
            <td>{html.escape(result['update_set_name'])}</td>
            <td>{html.escape(result['file_name'])}</td>
            <td>{result['score']}/100</td>
            <td><b>{html.escape(result['decision'])}</b></td>
            <td>
                <ul>{issue_items}</ul>
                <p><b>Summary:</b> {html.escape(result['ai_summary'])}</p>
            </td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Sync Smart AI - Day 1 Validation Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f7f7f7;
            }}
            h1 {{
                color: #333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 12px;
                vertical-align: top;
            }}
            th {{
                background: #eeeeee;
            }}
        </style>
    </head>
    <body>
        <h1>Sync Smart AI - Day 1 Validation Report</h1>
        <p>ServiceNow Update Set pre-sync validation report.</p>

        <table>
            <thead>
                <tr>
                    <th>Update Set</th>
                    <th>File</th>
                    <th>Confidence Score</th>
                    <th>Decision</th>
                    <th>Issues & Summary</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    """


def main():
    REPORTS_DIR.mkdir(exist_ok=True)

    baseline = load_baseline(BASELINE_FILE)
    results = []

    xml_files = sorted(UPDATE_SET_DIR.glob("*.xml"))

    if not xml_files:
        print("No update set XML files found in update_sets folder.")
        return

    for xml_file in xml_files:
        update_set = parse_update_set(xml_file)
        issues = validate_update_set(update_set, baseline)
        score, decision = calculate_score_and_decision(issues)
        ai_summary = generate_ai_summary(update_set, issues, score, decision)

        result = {
            "file_name": update_set["file_name"],
            "update_set_name": update_set["update_set_name"],
            "objects_count": len(update_set["objects"]),
            "issues": issues,
            "score": score,
            "decision": decision,
            "ai_summary": ai_summary
        }

        results.append(result)

        print("-----------------------------------")
        print(f"Update Set: {result['update_set_name']}")
        print(f"File: {result['file_name']}")
        print(f"Score: {score}/100")
        print(f"Decision: {decision}")
        print(f"Issues Found: {len(issues)}")

    json_report_path = REPORTS_DIR / "day1_validation_report.json"
    html_report_path = REPORTS_DIR / "validation_report.html"

    with open(json_report_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    with open(html_report_path, "w", encoding="utf-8") as file:
        file.write(build_html_report(results))

    print("-----------------------------------")
    print(f"JSON report generated: {json_report_path}")
    print(f"HTML report generated: {html_report_path}")


if __name__ == "__main__":
    main()