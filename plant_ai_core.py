def compute_overall_risk(perf_data, system_data, alert_data):
    score = 0

    if system_data["risk_level"] == "Moderate":
        score += 2
    elif system_data["risk_level"] == "High":
        score += 4

    if alert_data["risk_level"] == "Moderate":
        score += 2
    elif alert_data["risk_level"] == "High":
        score += 4

    if perf_data["pr_vs_target"] < 0:
        score += 2

    if score >= 6:
        return "High"
    elif score >= 3:
        return "Moderate"
    else:
        return "Low"