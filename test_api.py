from data_fetcher import (
    fetch_system_status,
    fetch_alerts,
    fetch_performance_metrics
)

if __name__ == "__main__":
    print("\nSYSTEM STATUS:")
    print(fetch_system_status())

    print("\nALERTS:")
    print(fetch_alerts())

    print("\nPERFORMANCE:")
    print(fetch_performance_metrics())