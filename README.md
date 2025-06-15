# Store Monitoring Modular Solution

## Directory Structure

```
store_monitoring/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   ├── db/
│   │   └── mongo.py
│   ├── models/
│   │   └── report.py
│   ├── services/
│   │   └── report_service.py
│   ├── utils/
│   │   ├── csv_utils.py
│   │   ├── interpolation.py
│   │   └── time_utils.py
│   └── config.py
├── data_loader.py
├── requirements.txt
├── README.md
```

## How to Run

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
2. **Load data:**
   - Place your CSVs in a `data/` folder: `store_status.csv`, `business_hours.csv`, `timezones.csv`
   - Run:
     ```
     python data_loader.py
     ```
3. **Start the API:**
   ```
   uvicorn app.main:app --reload
   ```
4. **Trigger a report:**
   ```
   curl -X POST localhost:8000/trigger_report
   ```
5. **Poll for report:**
   ```
   curl localhost:8000/get_report?report_id=YOUR_ID
   ```

## Output

- The output CSV will be placed in the `reports/` directory.
- Columns: `store_id, uptime_last_hour(in minutes), ... downtime_last_week(in hours)`

## Improvements

- Use a distributed task queue (Celery) for heavy workloads
- Pagination/streaming for large reports
- Authentication
- More flexible API filters (date, store)
- Unit and integration tests

## Sample Output

See `sample_report.csv`.