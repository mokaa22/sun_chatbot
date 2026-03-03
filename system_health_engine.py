def analyze_system_status(system_data):
    inverters_online = system_data["invertersOnline"]
    total_inverters = system_data["totalInverters"]

    strings_online = system_data["stringStatus"]
    total_strings = system_data["totalStrings"]

    inverter_availability = (inverters_online / total_inverters) * 100
    string_availability = (strings_online / total_strings) * 100

    communication = system_data["communication"]
    grid = system_data["gridConnection"]

    risk_level = calculate_risk(
        inverter_availability,
        string_availability,
        communication,
        grid
    )

    summary = generate_system_summary(
        inverter_availability,
        string_availability,
        communication,
        grid,
        risk_level
    )

    return {
        "inverter_availability": round(inverter_availability, 2),
        "string_availability": round(string_availability, 2),
        "risk_level": risk_level,
        "summary": summary
    }


def calculate_risk(inv_avail, str_avail, comm, grid):
    score = 0

    if inv_avail < 95:
        score += 2
    if str_avail < 98:
        score += 1
    if comm != "Online":
        score += 3
    if grid != "Stable":
        score += 3

    if score >= 5:
        return "High"
    elif score >= 2:
        return "Moderate"
    else:
        return "Low"


def generate_system_summary(inv_avail, str_avail, comm, grid, risk):
    summary = (
        f"Inverter availability at {inv_avail:.1f}%. "
        f"String availability at {str_avail:.1f}%. "
        f"Communication status: {comm}. "
        f"Grid connection: {grid}. "
        f"Overall operational risk: {risk}."
    )
    return summary