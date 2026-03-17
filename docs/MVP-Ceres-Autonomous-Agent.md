# Ceres MVP: Autonomous Campaign Intelligence

## Objective

Ceres is an autonomous agent for campaign intelligence and marketing optimization.
The MVP converts uploaded CSV campaign data into deterministic metrics and actionable insights.

## 1. Project Structure (in `ceres/`)

- `backend/` (FastAPI + analytics)
- `frontend/` (React/Vite dashboard)
- `agent/` (insights/routing layer)
- `data/` (sample CSVs, test data)
- `docs/` (specs and final documentation)

## 2. Data Ingestion

- Upload CSV with at least: `date`, `channel`, `spend`, `conversions`, `revenue`
- Parse and validate columns, types, duplicates
  -{error handling: missing fields, zero/negative values, parse failure}

## 3. Deterministic Metrics

Compute per channel and total:

- ROAS = revenue / spend
- ROI = (revenue - spend) / spend
- CPA = spend / conversions
- Conversion Rate = conversions / impressions (or fallback proxy)
- Trend delta (YoY/MoM/WoW change)

## 4. Anomaly Detection

- Sudden drop in conversions (e.g., >30% from previous period)
- Spike in CPA or drop in ROAS
- Missing weekly data points

## 5. Agent Insights Router

- Map user intent to tool:
  - “best channel” → top channel by ROAS
  - “worst channel” → bottom ROAS / ROI / CPA
  - “random” → auto analysis (balance, change, anomalies)
- Build grounded text output with evidence:
  - key metrics with thresholds
  - recommended budget reallocation (rule-based)

## 6. API Endpoints

- `POST /upload` -> accepts CSV, returns `run_id`
- `GET /metrics?run_id=<id>` -> computed metrics
- `GET /insights?run_id=<id>` -> generated insights
- `GET /ask?run_id=<id>&q=<question>` -> agent response

## 7. Frontend MVP

- CSV upload component
- Metrics table
- Visual charts (ROAS, spend/revenue, conversions)
- Insights panel
- Question input

## 8. Execution Plan

1. Setup backend scaffold + analytics module
2. Setup frontend skeleton + network requests
3. Add agent rules in backend `agent/`
4. Add sample dataset in `data/`
5. Test end-to-end with cURL + UI manual
6. Add tests: `pytest` + `jest`/`cypress`

## 9. Example insights

- “Channel paid_search ROAS 4.3 (best). Recommend shift 20% budget from display to paid_search.”
- “Channel social CPA $62 (worst) and 38% volume drop MoM. Investigate creatives and tracking.”
- “Conversion volume fell 45% last 7 days. Check attribution/landing experience.”

## 10. Deployment and validation

- Run `uvicorn backend.main:app --reload`
- Run `npm run dev` in frontend
- Confirm `POST /upload` works with sample CSV
- Validate agent text matches expected (Best/Worst/Anomaly)

---

### Notes

This file is the final MVP guide and should be kept updated as the product evolves.
