/* Weekly Active Users (WAU) & Feature Mix
  
  Goal:
  For each account and week, compute WAU (distinct active users), total events, and the top feature’s share of events. 
  Flag a simple anomaly when the top feature dominates beyond a threshold (e.g., 70%).
*/
WITH RECURSIVE weeks(metric_start) AS (
  SELECT '2024-07-01'
  UNION ALL
  SELECT ____
  FROM weeks
  WHERE metric_start < '2024-08-31'
),
totals AS (
  SELECT
    e.account_id,
    w.metric_start AS week_start,
    ____ AS wau,
    COUNT(*) AS total_events
  FROM events AS e
  JOIN weeks AS w
    ON e.event_time >= w.metric_start
   AND e.event_time < ____
  GROUP BY e.account_id, w.metric_start
),
per_type AS (
  SELECT
    e.account_id,
    w.metric_start AS week_start,
    e.event_type,
    COUNT(*) AS type_count
  FROM events AS e
  JOIN weeks AS w
    ON e.event_time >= w.metric_start
   AND e.event_time < ____
  GROUP BY e.account_id, w.metric_start, e.event_type
)
SELECT
  t.account_id,
  t.week_start,
  t.wau,
  MAX( (pt.type_count * 1.0) / t.total_events ) AS top_feature_pct_share,
  ____ AS top_feature,
  CASE
    WHEN MAX( (pt.type_count * 1.0) / t.total_events ) > ____ THEN 1
    ELSE 0
  END AS anomaly_flag
FROM totals AS t
JOIN per_type AS pt
  ON t.account_id = pt.account_id
 AND t.week_start = pt.week_start
GROUP BY t.account_id, t.week_start
ORDER BY t.account_id, t.week_start;