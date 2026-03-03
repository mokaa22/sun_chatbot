import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("SUNFLUENCE_API")
TOKEN = os.getenv("SUNFLUENCE_TOKEN")


def make_authenticated_get(endpoint):
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("API ERROR:", response.text)
        return {}

    return response.json()


# ----------------------------------
# DASHBOARD OVERVIEW (MAIN SUMMARY)
# ----------------------------------

def fetch_dashboard_overview():
    return make_authenticated_get("/farm/1/dashboard/overview")


# ----------------------------------
# ALERTS
# ----------------------------------

def fetch_alerts():
    return make_authenticated_get("/farm/1/dashboard/alerts")


# ----------------------------------
# REVENUE
# ----------------------------------

def fetch_revenue_tracking():
    return make_authenticated_get("/farm/1/energy/revenue-tracking")


# ----------------------------------
# (Optional legacy endpoints)
# ----------------------------------

def fetch_system_status():
    return make_authenticated_get("/farm/1/dashboard/system-status")


def fetch_performance_metrics():
    return make_authenticated_get("/farm/1/energy/performance-breakdown")


def fetch_environment_conditions():
    return make_authenticated_get("/farm/1/sensors/environment")