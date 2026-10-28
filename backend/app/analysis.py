
import pandas as pd
import numpy as np


def calculate_accuracy(actuals, forecasts):
    """
    Compare actual wind generation with the latest eligible forecast
    published by 10:00 UTC on the previous day.

    The 10:00 UTC cutoff is a project assumption and should be
    validated against the intended procurement decision time.
    """

    actual_df = pd.DataFrame(actuals)
    forecast_df = pd.DataFrame(forecasts)

    # Handle missing input data.
    if actual_df.empty or forecast_df.empty:
        return {
            "matched_periods": 0,
            "mae": None,
            "rmse": None,
            "bias": None,
            "message": "Not enough data to calculate accuracy.",
        }

    # Parse delivery and publication timestamps as UTC.
    actual_df["startTime"] = pd.to_datetime(
        actual_df["startTime"],
        utc=True,
        errors="coerce",
    )

    forecast_df["startTime"] = pd.to_datetime(
        forecast_df["startTime"],
        utc=True,
        errors="coerce",
    )

    forecast_df["publishTime"] = pd.to_datetime(
        forecast_df["publishTime"],
        utc=True,
        errors="coerce",
    )

    # Convert generation values to numeric data.
    actual_df["generation"] = pd.to_numeric(
        actual_df["generation"],
        errors="coerce",
    )

    forecast_df["generation"] = pd.to_numeric(
        forecast_df["generation"],
        errors="coerce",
    )

    # Remove records with missing or invalid values.
    actual_df = actual_df.dropna(
        subset=["startTime", "generation"]
    )

    forecast_df = forecast_df.dropna(
        subset=["startTime", "publishTime", "generation"]
    )

    # Keep one actual value for each delivery timestamp.
    actual_df = actual_df.drop_duplicates(
        subset=["startTime"],
        keep="last",
    )

    # Keep only forecasts published by the day-ahead cutoff.
    forecast_df["cutoff"] = (
        forecast_df["startTime"].dt.normalize()
        - pd.Timedelta(days=1)
        + pd.Timedelta(hours=10)
    )

    eligible = forecast_df[
        forecast_df["publishTime"] <= forecast_df["cutoff"]
    ].copy()

    if eligible.empty:
        return {
            "matched_periods": 0,
            "mae": None,
            "rmse": None,
            "bias": None,
            "message": (
                "No forecasts were available before the "
                "day-ahead cutoff."
            ),
        }

    # Select the latest eligible forecast for each delivery time.
    eligible = eligible.sort_values("publishTime")

    selected_forecasts = eligible.drop_duplicates(
        subset=["startTime"],
        keep="last",
    )

    # Match forecasts with actual generation at the same UTC time.
    merged = actual_df.merge(
        selected_forecasts[["startTime", "generation"]],
        on="startTime",
        how="inner",
        suffixes=("_actual", "_forecast"),
        validate="one_to_one",
    )

    if merged.empty:
        return {
            "matched_periods": 0,
            "mae": None,
            "rmse": None,
            "bias": None,
            "message": "No matching delivery periods found.",
        }

    # Positive errors indicate that generation was overforecast.
    errors = (
        merged["generation_forecast"]
        - merged["generation_actual"]
    )

    mae = errors.abs().mean()
    rmse = np.sqrt((errors ** 2).mean())
    bias = errors.mean()

    return {
        "matched_periods": int(len(merged)),
        "mae": round(float(mae), 2),
        "rmse": round(float(rmse), 2),
        "bias": round(float(bias), 2),
    }
