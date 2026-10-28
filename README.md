# WindScope — Wind Forecast Analytics Dashboard

WindScope is a full-stack web application for analyzing wind power forecasts and actual wind generation in the UK electricity market. It helps users compare day-ahead forecasts with actual generation, understand forecast errors, and explore historical forecast publication data to support electricity procurement decisions.

## Live Demo

- **Live Dashboard:** https://windscope-wind-forecast-dashboard.vercel.app/
- **Backend API:** https://windscope-wind-forecast-dashboard.onrender.com/
- **API Health Check:** https://windscope-wind-forecast-dashboard.onrender.com/health
- **Forecast Accuracy API:** https://windscope-wind-forecast-dashboard.onrender.com/api/accuracy
- **GitHub Repository:** https://github.com/chsnehith/windscope-wind-forecast-dashboard

## Features

- **Forecast vs Actual Comparison:** Visualizes day-ahead wind generation forecasts alongside actual generation.
- **Forecast Accuracy Metrics:** Displays Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), forecast bias, and matched periods.
- **Day-Ahead Forecast Selection:** Selects the most recently published eligible forecast for each delivery timestamp, using a configurable project cutoff.
- **Publication Details:** Displays delivery timestamps, forecast publication timestamps, and forecast generation values.
- **Interactive Dashboard:** Includes responsive metric cards, line charts, tooltips, and a refresh option.
- **REST API:** Provides endpoints for actual generation, forecasts, health checks, and accuracy metrics.
- **Docker Support:** Includes Dockerfiles and Docker Compose configuration for local development.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| UI and Charts | CSS, Recharts, Lucide React |
| Backend | Python, FastAPI, Uvicorn |
| Data Processing | Pandas, NumPy |
| Data Source | Elexon BMRS |
| Containerization | Docker, Docker Compose |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |
| Version Control | Git, GitHub |

## Architecture

```text
                    Elexon BMRS
                         |
                         v
                  FastAPI Backend
                    (Render)
                         |
              REST API endpoints
                         |
                         v
                  React Frontend
                    (Vercel)
                         |
                         v
              WindScope Dashboard
              - Accuracy metrics
              - Forecast vs actual
              - Publication details
```

The frontend requests data from the deployed FastAPI backend. The backend retrieves and processes wind generation data and exposes it through REST API endpoints. The frontend then displays the returned data using metric cards, tables, and interactive charts.

## Data and Evaluation Period

The current dashboard analyzes **January 2026** data.

The application uses wind generation actuals and forecast records obtained from Elexon BMRS. Forecast publication timestamps are used to select forecasts that would have been available before the assumed day-ahead decision cutoff.

### Day-Ahead Cutoff Assumption

The current implementation uses **10:00 UTC on the day before delivery** as the assumed forecast selection cutoff.

For each delivery timestamp, the application excludes forecasts published after this cutoff and selects the most recently published eligible forecast.

This is a project assumption and should be validated against the intended electricity procurement decision time before using the results for operational decisions.

## Forecast Accuracy Metrics

The deployed dashboard currently reports the following January 2026 results:

| Metric | Value |
|---|---:|
| Matched Periods | 744 |
| Mean Absolute Error (MAE) | 2,107.18 |
| Root Mean Squared Error (RMSE) | 2,611.24 |
| Forecast Bias | 1,839.92 |

**Metric interpretation:**

- **Matched Periods:** Number of forecast and actual timestamps matched for evaluation.
- **MAE:** Average absolute difference between forecast and actual generation.
- **RMSE:** Measures forecast error while giving greater weight to larger errors.
- **Forecast Bias:** Indicates the direction of average forecast error. A positive value represents overforecasting under the application's calculation convention.

The unit is currently reported as provided by Elexon. These values should not be interpreted as MW until the source units and calculations have been verified.

## REST API Endpoints

Base URL:

```text
https://windscope-wind-forecast-dashboard.onrender.com
```

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status message |
| GET | `/health` | Backend health check |
| GET | `/api/actuals` | Actual wind generation data |
| GET | `/api/forecasts` | Wind forecast records, including revisions |
| GET | `/api/accuracy` | Forecast accuracy metrics |

### Example Response: Health Check

Request:

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

### Example Response: Forecast Accuracy

Request:

```http
GET /api/accuracy
```

Example response:

```json
{
  "period": "January 2026",
  "unit": "As provided by Elexon",
  "matched_periods": 744,
  "mae": 2107.18,
  "rmse": 2611.24,
  "bias": 1839.92
}
```

## Run Locally with Docker

### Prerequisites

Install the following tools:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 1. Clone the Repository

```bash
git clone https://github.com/chsnehith/windscope-wind-forecast-dashboard.git
cd windscope-wind-forecast-dashboard
```

### 2. Start the Application

From the project root, run:

```bash
docker compose up --build
```

Docker Compose builds and starts both the frontend and backend services.

### 3. Open the Application

- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:8000
- **API Health Check:** http://localhost:8000/health
- **Forecast Accuracy:** http://localhost:8000/api/accuracy

To stop the services, press `Ctrl + C` and run:

```bash
docker compose down
```

## Project Structure

```text
windscope-wind-forecast-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── elexon.py
│   │   └── analysis.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── vite.config.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Deployment

The application is deployed as two separate services:

**Frontend — Vercel**

The React and Vite application is deployed from the `frontend` directory of the GitHub repository.

**Backend — Render**

The FastAPI application is deployed from the `backend` directory using its Dockerfile.

The backend's CORS configuration allows requests from the deployed Vercel domain and the configured local development origins.

The free Render service may spin down after inactivity, so the first request after a period of inactivity can take longer than usual.

## Limitations and Future Improvements

- Validate the assumed 10:00 UTC forecast cutoff against the intended procurement workflow.
- Confirm the source units and document the units used in accuracy calculations.
- Verify that actuals and forecasts represent the same delivery intervals and aggregation levels.
- Evaluate additional forecast error metrics and performance across different periods.
- Add date-range selection and more detailed forecast error analysis.
- Improve API error handling, caching, and data retrieval efficiency.
- Add automated tests and a continuous integration workflow.
- Improve dashboard accessibility and responsive behavior across screen sizes.

## Disclaimer

WindScope is an analytical and demonstration project. The displayed results are intended for exploration and evaluation, not as a standalone basis for real-world electricity trading or procurement decisions. Data availability, source units, timestamp alignment, and forecast selection assumptions should be validated before operational use.

## Author

**Snehith Chilukamari**

B.Tech in Computer Science and Engineering

GitHub: https://github.com/chsnehith

---

*Built to explore wind generation forecasting, forecast accuracy evaluation, and data-driven energy procurement analysis.*