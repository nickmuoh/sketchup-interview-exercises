/* Viral Loop Analysis: Monthly Net-New Viral Lift

Goal: For each month, calculate the average number of net-new (unknown) users
invited per unique shared file, and flag months where role counts are inconsistent.
*/
WITH
  base_flattened AS (
    SELECT
      event_time,
      STRFTIME ('%Y-%m', event_time) AS event_month,
      json_extract (event_properties, '$.file_id') AS file_id,
      json_extract (event_properties, '$.share_metadata.recipients_count') AS total_recipients,
      json_extract (event_properties, '$.share_metadata.identity_stats.unknown_contacts') AS net_new_invites,
      json_extract (event_properties, '$.share_metadata.role_distribution.editors') AS n_editors,
      json_extract (event_properties, '$.share_metadata.role_distribution.commenters') AS n_commenters,
      json_extract (event_properties, '$.share_metadata.role_distribution.viewers') AS n_viewers
    FROM
      product_telemetry
    WHERE
      event_type = 'share_invite_sent'
      AND event_time >= '2025-01-01'
  ),
  monthly_metrics AS (
    SELECT
      event_month,
      COUNT(DISTINCT file_id) AS monthly_unique_files,
      SUM(total_recipients) AS monthly_total_recipients,
      SUM(net_new_invites) AS monthly_net_new,
      SUM(n_editors) AS total_editors,
      SUM(n_commenters) AS total_commenters,
      SUM(n_viewers) AS total_viewers
    FROM
      base_flattened
    GROUP BY
      event_month
  )
SELECT
  event_month,
  monthly_unique_files,
  CASE
    WHEN monthly_unique_files = 0 THEN 0
    ELSE monthly_net_new * 1.0 / monthly_unique_files
  END AS net_new_viral_lift,
  CASE
    WHEN (total_editors + total_commenters + total_viewers) = monthly_total_recipients THEN 1
    ELSE 0
  END AS is_instrumentation_valid
FROM
  monthly_metrics
ORDER BY
  event_month DESC;
