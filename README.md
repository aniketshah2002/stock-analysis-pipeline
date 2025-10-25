# NIFTY 50 Stock Analysis Dashboard

**[➡️ Click here to view the Live Dashboard](https://lookerstudio.google.com/reporting/df88b94f-ed91-4f62-941b-2d8ab614e24c)**

---

### Project Overview

This project is an end-to-end data pipeline that automates the collection of stock data from the Indian National Stock Exchange (NSE), processes it, and visualizes key technical indicators in an interactive dashboard.

The goal was to build a hands-on project demonstrating skills in data engineering, cloud data warehousing, advanced SQL analysis, and business intelligence (BI).

### Tech Stack

* **Data Collection:** Python (`yfinance`, `pandas`)
* **Data Warehouse:** Google BigQuery
* **Data Transformation:** SQL (Window Functions, CTEs)
* **Data Visualization:** Google Looker Studio
* **Authentication:** Google Cloud SDK (`gcloud`)

---

### Project Workflow

1.  **Data Extraction:** A Python script (`get_data.py`) uses the `yfinance` library to download 5 years of daily stock data for the NIFTY 50.
2.  **Data Loading:** The script uploads this data directly into a Google BigQuery table using the `pandas-gbq` library, authenticating via the Google Cloud SDK.
3.  **Data Transformation:** A BigQuery **View** (`stock_analytics_view.sql`) is layered on top of the raw data. This SQL query uses **Window Functions** to calculate advanced indicators:
    * 30-day and 200-day Simple Moving Averages (SMA)
    * 20-day Bollinger Bands (SMA + 2x Standard Deviation)
    * "Golden Cross" and "Death Cross" buy/sell signals
4.  **Data Visualization:** The clean, transformed data from the BigQuery View is connected to a Looker Studio dashboard, which provides interactive filters and charts.

---

### Dashboard Screenshot

`![Dashboard Screenshot](stock-analysis-dashboard.png)`

---

### Advanced SQL Analysis

The core logic of this project lives in the SQL View. This query transforms raw daily prices into actionable insights.

```sql
-- This is the full query from stock_analytics_view.sql
WITH daily_data AS (
  SELECT
    date,
    Ticker,
    close,
    LAG(close, 1) OVER (PARTITION BY Ticker ORDER BY date) AS prev_day_close
  FROM
    `stock-dashboard-project-476115.stock_analysis.raw_stock_data`
),

moving_calcs AS (
  SELECT
    *,
    -- 20-day SMA (for Bollinger)
    AVG(close) OVER (
      PARTITION BY Ticker
      ORDER BY date
      ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS sma_20_day,
    
    -- 20-day Standard Deviation (for Bollinger)
    STDDEV(close) OVER (
      PARTITION BY Ticker
      ORDER BY date
      ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS std_dev_20_day,
    
    -- 30-day and 200-day for your Crossover
    AVG(close) OVER (
      PARTITION BY Ticker
      ORDER BY date
      ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS sma_30_day,
    
    AVG(close) OVER (
      PARTITION BY Ticker
      ORDER BY date
      ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
    ) AS sma_200_day
  FROM
    daily_data
),
-- ... (paste the rest of your query here) ...


