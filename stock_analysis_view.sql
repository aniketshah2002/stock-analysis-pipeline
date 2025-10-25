WITH
    daily_data
    AS
    (
        SELECT
            date,
            Ticker,
            close,
            LAG(close, 1) OVER (PARTITION BY Ticker ORDER BY date) AS prev_day_close
        FROM
            `stock
    -dashboard-project-476115.stock_analysis.raw_stock_data` 
),

moving_calcs AS
(
  SELECT
    *,
    -- 20-day SMA (for Bollinger)\
    AVG(
close) OVER
(
      PARTITION BY Ticker
      ORDER BY date
      ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS sma_20_day,
    
    -- 20-day Standard Deviation (for Bollinger)
    STDDEV
(
close) OVER
(
      PARTITION BY Ticker 
      ORDER BY date
      ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS std_dev_20_day,
    
    -- 30-day and 200-day for your Crossover
    AVG
(
close) OVER
(
      PARTITION BY Ticker 
      ORDER BY date
      ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS sma_30_day,
    
    AVG
(
close) OVER
(
      PARTITION BY Ticker
      ORDER BY date
      ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
    ) AS sma_200_day
  FROM
    daily_data
),

signals AS
(
  SELECT
    *,
    -- Bollinger Bands
    (sma_20_day + (2 * std_dev_20_day)) AS bollinger_upper_band,
    (sma_20_day - (2 * std_dev_20_day)) AS bollinger_lower_band,

    -- Crossover Signals
    CASE
      WHEN sma_30_day > sma_200_day AND LAG(sma_30_day, 1) OVER (PARTITION BY Ticker ORDER BY date) <= LAG(sma_200_day, 1) OVER (PARTITION BY Ticker ORDER BY date)
      THEN 'Golden Cross (Buy)'
      WHEN sma_30_day < sma_200_day AND LAG(sma_30_day, 1) OVER (PARTITION BY Ticker ORDER BY date) >= LAG(sma_200_day, 1) OVER (PARTITION BY Ticker ORDER BY date)
      THEN 'Death Cross (Sell)'
    ELSE
      NULL
    END AS signal
FROM
    moving_calcs
)

-- Final SELECT to create the view
SELECT
    date,
    Ticker, 
close,
  sma_30_day,
  sma_200_day,
  sma_20_day,
  bollinger_upper_band,
  bollinger_lower_band,
  signal
FROM
  signals;