# WindScope â€” Wind Forecast Analytics Dashboard

WindScope is a full-stack dashboard for exploring historical UK wind generation forecasts and comparing them with actual
generation. It uses data from the Elexon BMRS API to help understand forecast error and uncertainty in day-ahead electricity 
procurement.

## Features
- Retrieves historical wind generation actuals and forecasts from Elexon BMRS.
- Compares day-ahead forecasts with actual generation.
- Displays Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), forecast bias, and matched periods.
- Visualizes forecasts and actual generation using an interactive chart.
- Displays forecast publication timestamps and historical revisions.
- Runs locally using Docker Compose.

## Technology Stack
**Frontend:** React, Vite, Recharts, Lucide React  
**Backend:** Python, FastAPI, Pandas, NumPy  
**Data source:** Elexon BMRS API  
**Containerization:** Docker, Docker Compose

## Project Structure

```text
wind-forecast-dashboard/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ analysis.py
â”‚   â”‚   â”œâ”€â”€ elexon.py
â”‚   â”‚   â””â”€â”€ main.py
â”‚   â”œâ”€â”€ Dockerfile
â”‚   â””â”€â”€ requirements.txt
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ App.jsx
â”‚   â”‚   â”œâ”€â”€ App.css
â”‚   â”‚   â””â”€â”€ main.jsx
â”‚   â”œâ”€â”€ Dockerfile
â”‚   â”œâ”€â”€ package.json
â”‚   â””â”€â”€ vite.config.js
â”œâ”€â”€ docker-compose.yml
â””â”€â”€ README.md
```

## Requirements
- Docker Desktop
- Docker Compose

## Run the Project
1. Clone this repository.
2. Open a terminal in the project directory.
3. Build and start the services:

```bash
docker compose up --build
```

4. Open the dashboard at http://localhost:5173.
5. Check backend health at http://localhost:8000/health.
6. View forecast accuracy at http://localhost:8000/api/accuracy.

To stop the services, press `Ctrl+C` in the terminal running Docker Compose. If they were started in detached mode, run:

```bash
docker compose down
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `/health` | Checks backend health |
| `/api/actuals` | Returns actual wind generation data |
| `/api/forecasts` | Returns historical wind forecasts |
| `/api/accuracy` | Returns forecast accuracy metrics |

## Forecast Evaluation

The dashboard reports:

- **Matched periods:** Number of delivery timestamps with matching forecast and actual values.
- **MAE:** Average absolute difference between forecast and actual generation.
- **RMSE:** Square root of the average squared forecast error, giving larger errors more weight.
- **Forecast bias:** Mean of forecast minus actual generation. Positive bias indicates overforecasting.

The current analysis uses a project-assumed cutoff of 10:00 UTC on the day before delivery. For each delivery timestamp, it 
selects the latest forecast published by that cutoff. This assumption should be validated against the intended procurement 
decision time before operational use.

The metrics depend on timestamp alignment, data availability, and the units provided by Elexon. They are intended for 
exploratory analysis, not as a guarantee of trading or procurement outcomes.

## Data Source
Historical wind generation data is retrieved from the Elexon BMRS API.

Official website: https://www.elexon.co.uk/

## Limitations

- The current dashboard analyzes January 2026 data.
- The 10:00 UTC day-ahead cutoff is a project assumption, not a verified market deadline.
- Forecast accuracy alone does not determine an optimal electricity procurement strategy.
- Generation units and timestamp alignment should be confirmed against source API documentation before operational use.

## Development Notes

The frontend uses Vite's development server and proxy to forward `/api` requests to the FastAPI backend when running through 
Docker Compose.

For local development without Docker, configure the frontend API connection for the local backend before starting Vite.

## AI Assistance

AI tools were used to assist with parts of the development and documentation process. The implementation, configuration, and 
results should be reviewed and validated before production use.

