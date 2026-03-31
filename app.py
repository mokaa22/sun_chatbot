import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from data_fetcher import (
    fetch_dashboard_overview,
    fetch_system_status,
    fetch_alerts,
    fetch_revenue_tracking
)

from groq_engine import generate_ai_response, SYSTEM_PROMPT

load_dotenv()
app = Flask(__name__)

chat_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# ---------------------------------
# Language Detection
# ---------------------------------
def detect_language_style(user_message):
    msg = user_message.lower()

    gujarati_keywords = ["kem", "tame", "maru", "su", "chu", "che"]
    hindi_keywords = ["kaise", "kya", "kyu", "mera", "hai"]

    words = msg.split()

    if any(word in words for word in gujarati_keywords):
        return "Gujarati (Roman script only)"

    if any(word in words for word in hindi_keywords):
        return "Hindi (Roman script only)"

    return "English"


# ---------------------------------
# Safe Getter
# ---------------------------------
def safe_get(data, *keys):
    if not isinstance(data, dict):
        return None
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return None


# ---------------------------------
# KPI Extraction (UNCHANGED)
# ---------------------------------
def extract_kpis(overview_data, system_data, revenue_data):

    kpis = {}

    total_inv = safe_get(system_data, "totalInverters") or 0
    online_inv = safe_get(system_data, "invertersOnline") or 0

    if total_inv > 0:
        kpis["offline_inverter_percent"] = round(
            ((total_inv - online_inv) / total_inv) * 100, 2
        )
    else:
        kpis["offline_inverter_percent"] = "Unavailable"

    total_strings = safe_get(system_data, "totalStrings") or 0
    active_strings = safe_get(system_data, "stringStatus") or 0

    if total_strings > 0:
        kpis["string_loss_percent"] = round(
            ((total_strings - active_strings) / total_strings) * 100, 2
        )
    else:
        kpis["string_loss_percent"] = "Unavailable"

    kpis["grid_status"] = safe_get(system_data, "gridConnection", "gridStatus") or "Unavailable"

    irr_obj = (
        overview_data.get("irradiance")
        or overview_data.get("currentIrradiance")
        or overview_data.get("solarIrradiance")
    )

    if isinstance(irr_obj, dict):
        kpis["irradiance"] = irr_obj.get("value", "Unavailable")
    else:
        kpis["irradiance"] = irr_obj if irr_obj else "Unavailable"

    gen_obj = (
        overview_data.get("currentGeneration")
        or overview_data.get("currentPower")
        or overview_data.get("todayEnergy")
    )

    if isinstance(gen_obj, dict):
        kpis["generation"] = gen_obj.get("value", "Unavailable")
    else:
        kpis["generation"] = gen_obj if gen_obj else "Unavailable"

    kpis["todays_revenue"] = revenue_data.get("todaysRevenue") or "Unavailable"
    kpis["monthly_revenue"] = revenue_data.get("monthlyRevenue") or "Unavailable"
    kpis["energy_rate"] = revenue_data.get("energyRate") or "Unavailable"

    return kpis


# ---------------------------------
# DOMAIN FILTER (NEW 🔥)
# ---------------------------------
def is_solar_related(message):
    keywords = [
        "solar", "plant", "generation", "irradiance", "grid",
        "revenue", "energy", "performance", "pr", "cuf",
        "loss", "efficiency", "inverter", "string"
    ]
    msg = message.lower()
    return any(word in msg for word in keywords)


# ---------------------------------
# Routes
# ---------------------------------
@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/ai-chat", methods=["POST"])
def ai_chat():
    global chat_history

    try:
        user_message = request.json.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please enter a valid query."})

        lower_msg = user_message.lower()

        # ---------------------------------
        # Greeting
        # ---------------------------------
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        if lower_msg in greetings:
            return jsonify({
                "reply": "Hi! Welcome to Sunfluence AI Assistant ☀️\nHow can I assist you with your solar plant today?"
            })

        # ---------------------------------
        # Small Talk
        # ---------------------------------
        small_talk = ["ok", "okay", "got it", "thanks", "thank you", "fine", "cool", "great"]
        if lower_msg in small_talk:
            return jsonify({
                "reply": "Understood. Let me know if you'd like to analyze any specific parameter."
            })

        # ---------------------------------
        # ❌ DOMAIN RESTRICTION (NEW 🔥)
        # ---------------------------------
        if not is_solar_related(user_message):
            return jsonify({
                "reply": "😊 Sorry, I can only assist with solar plant data, performance, and related insights. Please ask something related to your plant."
            })

        # ---------------------------------
        # SNAPSHOT
        # ---------------------------------
        snapshot_keywords = [
            "live plant data",
            "current plant status",
            "full status",
            "plant snapshot",
            "live status"
        ]

        if lower_msg in snapshot_keywords:

            overview_data = fetch_dashboard_overview() or {}
            system_data = fetch_system_status() or {}
            revenue_data = fetch_revenue_tracking() or {}
            alerts_data = fetch_alerts() or []

            kpis = extract_kpis(overview_data, system_data, revenue_data)

            if isinstance(alerts_data, list) and len(alerts_data) > 0:
                formatted_alerts = ""
                for alert in alerts_data:
                    title = alert.get("title", "Unknown Alert")
                    severity = alert.get("severity", "info").capitalize()
                    formatted_alerts += f"- {title} ({severity})\n"
            else:
                formatted_alerts = "No active alerts."

            reply = f"""
Here is the current live plant snapshot:

Offline Inverter %: {kpis['offline_inverter_percent']}%
String Loss %: {kpis['string_loss_percent']}%
Grid Status: {kpis['grid_status']}
Current Irradiance: {kpis['irradiance']} W/m²
Current Generation: {kpis['generation']} kW
Today's Revenue: ₹ {kpis['todays_revenue']}
Monthly Revenue: ₹ {kpis['monthly_revenue']}
Energy Rate: ₹ {kpis['energy_rate']}/kWh

Active Alerts:
{formatted_alerts}
"""
            return jsonify({"reply": reply.strip()})

        # ---------------------------------
        # ANALYTICAL MODE (LLM)
        # ---------------------------------
        overview_data = fetch_dashboard_overview() or {}
        system_data = fetch_system_status() or {}
        revenue_data = fetch_revenue_tracking() or {}
        alerts_data = fetch_alerts() or []

        kpis = extract_kpis(overview_data, system_data, revenue_data)

        structured_context = f"""
User language style: {detect_language_style(user_message)}

LIVE KPI DATA:
Offline Inverter %: {kpis['offline_inverter_percent']}
String Loss %: {kpis['string_loss_percent']}
Grid Status: {kpis['grid_status']}
Current Irradiance: {kpis['irradiance']}
Current Generation: {kpis['generation']}
Today's Revenue: {kpis['todays_revenue']} ₹
Monthly Revenue: {kpis['monthly_revenue']} ₹
Energy Rate: {kpis['energy_rate']} ₹/kWh

Active Alerts: {alerts_data}

Respond only to the user's question.
Do not repeat full snapshot unless asked.
Do not invent numbers.
"""

        chat_history.append({
            "role": "user",
            "content": structured_context + "\n\nUser Question:\n" + user_message
        })

        ai_reply = generate_ai_response(chat_history)

        chat_history.append({
            "role": "assistant",
            "content": ai_reply
        })

        return jsonify({"reply": ai_reply})

    except Exception as e:
        print("SERVER ERROR:", str(e))
        return jsonify({
            "reply": "System error occurred while processing your request."
        })


if __name__ == "__main__":
    app.run(debug=True)
