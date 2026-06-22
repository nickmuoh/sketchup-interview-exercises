/* Subscription State Reconstruction (SCD2)

Goal:
Transform a raw stream of entitlement actions into continuous effective-date
windows for active subscription periods only.
*/
WITH state_transitions AS (
  SELECT
    user_id,
    entitlement_sku,
    action,
    DATE(event_time) AS state_start_date,

    -- 1. Look ahead to the date of the next state change for the user
    ____(DATE(event_time)) OVER(
      PARTITION BY ____
      ORDER BY event_time
    ) AS next_state_date
  FROM ems_events_projected
),
scd2_timeline AS (
  SELECT
    user_id,
    entitlement_sku,
    state_start_date AS effective_start_date,

    -- 2. Determine the end date of the current state
    CASE
      WHEN next_state_date IS NULL THEN '2050-12-31'
      ELSE DATE(____, '-1 day')
    END AS effective_end_date,
    action
  FROM state_transitions
)
SELECT
  user_id,
  entitlement_sku,
  effective_start_date,
  effective_end_date
FROM scd2_timeline
-- 3. Surface only active periods. Remove terminal states.
WHERE action ____ ('revoked', 'expired')
  -- 4. Final safety check: ensure start is <= end
  AND ____ <= ____
ORDER BY user_id, effective_start_date;
