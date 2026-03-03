from datetime import datetime

def analyze_alerts(alerts_data):
    critical_count = 0
    warning_count = 0

    inverter_issues = 0
    temperature_issues = 0
    string_issues = 0

    for alert in alerts_data:
        severity = alert["severity"]
        title = alert["title"].lower()

        if severity == "error":
            critical_count += 1
        elif severity == "warning":
            warning_count += 1

        if "inverter" in title:
            inverter_issues += 1
        if "temperature" in title:
            temperature_issues += 1
        if "string" in title:
            string_issues += 1

    risk_level = calculate_alert_risk(critical_count, warning_count)

    summary = generate_alert_summary(
        critical_count,
        warning_count,
        inverter_issues,
        string_issues,
        temperature_issues,
        risk_level
    )

    return {
        "critical_alerts": critical_count,
        "warning_alerts": warning_count,
        "risk_level": risk_level,
        "summary": summary
    }


def calculate_alert_risk(critical, warning):
    score = (critical * 3) + (warning * 1)

    if score >= 6:
        return "High"
    elif score >= 3:
        return "Moderate"
    else:
        return "Low"


def generate_alert_summary(critical, warning, inv, string, temp, risk):
    return (
        f"{critical} critical alerts and {warning} warnings active. "
        f"Inverter issues: {inv}, String issues: {string}, "
        f"Temperature alerts: {temp}. "
        f"Alert-based operational risk: {risk}."
    )