def analyze_trends(performance_data, pr_target=85, cuf_target=24):
    latest = performance_data[-1]
    first = performance_data[0]

    pr_growth = latest["performanceRatio"] - first["performanceRatio"]
    cuf_growth = latest["cuf"] - first["cuf"]

    pr_vs_target = latest["performanceRatio"] - pr_target
    cuf_vs_target = latest["cuf"] - cuf_target

    trend_summary = generate_summary(
        pr_growth,
        cuf_growth,
        pr_vs_target,
        cuf_vs_target,
        latest
    )

    return {
        "latest_month": latest["month"],
        "pr_growth": pr_growth,
        "cuf_growth": cuf_growth,
        "pr_vs_target": pr_vs_target,
        "cuf_vs_target": cuf_vs_target,
        "summary": trend_summary
    }


def generate_summary(pr_growth, cuf_growth, pr_vs_target, cuf_vs_target, latest):
    summary = f"In {latest['month']}, PR reached {latest['performanceRatio']}% and CUF reached {latest['cuf']}%.\n"

    if pr_growth > 0:
        summary += f"PR improved by {pr_growth}% since start of year. "

    if cuf_growth > 0:
        summary += f"CUF improved by {cuf_growth}% since start of year. "

    if pr_vs_target > 0:
        summary += f"PR is {pr_vs_target}% above target. "

    if cuf_vs_target > 0:
        summary += f"CUF is {cuf_vs_target}% above annual target. "

    return summary