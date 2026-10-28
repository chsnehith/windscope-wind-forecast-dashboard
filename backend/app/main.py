
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.elexon import fetch_wind_actuals, fetch_wind_forecasts
from app.analysis import calculate_accuracy

app = FastAPI(
    title="Wind Forecast Analytics API",
    description="UK wind generation forecast and accuracy analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://windscope-wind-forecast-dashboard.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Wind Forecast Analytics API is running",
        "status": "success",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/actuals")
def get_actuals():
    try:
        data = fetch_wind_actuals()
        return {
            "period": "January 2026",
            "count": len(data),
            "data": data,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to retrieve actual wind generation: {exc}",
        ) from exc


@app.get("/api/forecasts")
def get_forecasts():
    try:
        data = fetch_wind_forecasts()
        return {
            "period": "January 2026",
            "count": len(data),
            "data": data,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to retrieve wind forecasts: {exc}",
        ) from exc


@app.get("/api/accuracy")
def get_accuracy():
    try:
        actuals = fetch_wind_actuals()
        forecasts = fetch_wind_forecasts()

        result = calculate_accuracy(actuals, forecasts)

        return {
            "period": "January 2026",
            "unit": "As provided by Elexon",
            **result,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to calculate forecast accuracy: {exc}",
        ) from exc
