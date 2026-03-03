def analyze_system(system_data):
    online = system_data["invertersOnline"]
    total = system_data["totalInverters"]

    availability = round((online / total) * 100, 2)

    if availability < 95:
        risk = "High"
    elif availability < 98:
        risk = "Moderate"
    else:
        risk = "Low"

    return {
        "availability": availability,
        "risk": risk
    }


def analyze_alerts(alerts):
    critical = sum(1 for a in alerts if a["severity"] == "error")
    warnings = sum(1 for a in alerts if a["severity"] == "warning")

    if critical >= 2:
        risk = "High"
    elif critical == 1:
        risk = "Moderate"
    else:
        risk = "Low"

    return {
        "critical": critical,
        "warnings": warnings,
        "risk": risk
    }


def analyze_performance(performance_data):
    latest = performance_data[-1]

    pr = latest["performanceRatio"]
    cuf = latest["cuf"]

    if pr >= 90:
        performance_status = "Excellent"
    elif pr >= 85:
        performance_status = "Good"
    else:
        performance_status = "Needs Attention"

    return {
        "month": latest["month"],
        "pr": pr,
        "cuf": cuf,
        "status": performance_status
    }


def generate_chat_response(query, system_data, alerts_data, performance_data):
    system = analyze_system(system_data)
    alerts = analyze_alerts(alerts_data)
    performance = analyze_performance(performance_data)

    q = query.lower()

    if "risk" in q:
        if alerts["risk"] == "High" or system["risk"] == "High":
            return "Overall operational risk is HIGH due to active critical alerts."
        elif alerts["risk"] == "Moderate":
            return "Operational risk is MODERATE. Some alerts need attention."
        else:
            return "Operational risk is LOW. Plant running stable."

    elif "inverter" in q:
        return f"Inverter availability is {system['availability']}%. Current risk level: {system['risk']}."

    elif "alert" in q:
        return f"There are {alerts['critical']} critical alerts and {alerts['warnings']} warnings."

    elif "performance" in q or "pr" in q:
        return f"In {performance['month']}, PR is {performance['pr']}% and CUF is {performance['cuf']}%. Performance status: {performance['status']}."

    else:
        return (
            f"Plant status summary:\n"
            f"Inverter availability: {system['availability']}%\n"
            f"Critical alerts: {alerts['critical']}\n"
            f"Latest PR: {performance['pr']}%\n"
            f"Overall condition requires monitoring."
        )