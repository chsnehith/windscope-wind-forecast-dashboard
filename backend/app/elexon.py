
import time
import requests
from datetime import date, datetime, timedelta, timezone

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

START = datetime(2026, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 2, 1, tzinfo=timezone.utc)

SESSION = requests.Session()


def parse_time(value):
    """Convert an ISO timestamp into a timezone-aware datetime."""
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def is_january(value):
    timestamp = parse_time(value)
    return timestamp is not None and START <= timestamp < END


def fetch_wind_actuals():
    """Retrieve actual national wind generation for January 2026."""
    url = f"{BASE_URL}/datasets/FUELHH/stream"

    response = SESSION.get(
        url,
        params={
            "publishDateTimeFrom": "2026-01-01T00:00:00Z",
            "publishDateTimeTo": "2026-02-01T00:00:00Z",
        },
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()
    records = payload.get("data", []) if isinstance(payload, dict) else payload

    actuals = [
        {
            "startTime": row.get("startTime"),
            "generation": row.get("generation"),
        }
        for row in records
        if row.get("fuelType") == "WIND"
        and is_january(row.get("startTime"))
        and row.get("generation") is not None
    ]

    actuals.sort(key=lambda row: row["startTime"])
    return actuals


def fetch_wind_forecasts():
    """
    Retrieve historical wind forecast snapshots published at 09:30 UTC.

    The snapshots run from 31 December 2025 through 31 January 2026
    to include forecasts potentially available for 1 January delivery.
    """
    url = f"{BASE_URL}/forecast/generation/wind/history"

    first_date = date(2025, 12, 31)
    last_date = date(2026, 1, 31)

    forecasts_by_key = {}
    current_date = first_date

    while current_date <= last_date:
        publish_time = datetime(
            current_date.year,
            current_date.month,
            current_date.day,
            9,
            30,
            tzinfo=timezone.utc,
        )

        try:
            response = SESSION.get(
                url,
                params={"publishTime": publish_time.isoformat()},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()

            if isinstance(payload, dict):
                records = payload.get("data", [])
            else:
                records = payload

            for row in records:
                start_time = row.get("startTime")
                actual_publish_time = row.get("publishTime")
                generation = row.get("generation")

                if not is_january(start_time):
                    continue

                if generation is None or not actual_publish_time:
                    continue

                key = (start_time, actual_publish_time)

                forecasts_by_key[key] = {
                    "startTime": start_time,
                    "publishTime": actual_publish_time,
                    "generation": generation,
                }

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to fetch forecast published on "
                f"{publish_time.isoformat()}: {exc}"
            ) from exc

        current_date += timedelta(days=1)
        time.sleep(0.15)

    forecasts = list(forecasts_by_key.values())
    forecasts.sort(
        key=lambda row: (row["startTime"], row["publishTime"])
    )

    return forecasts
