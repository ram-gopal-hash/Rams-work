-- Solar generation analytics. Run: sqlite3 solar.db < queries.sql
-- Each query answers one question an asset owner asks every month.
.headers on
.mode column

-- Q1. Does the billing meter agree with the inverters?
-- Normal AC-side loss to the meter is c. 1-2.5%. Above 3% is a meter, CT or cabling question
-- worth raising before the invoice goes out, because the invoice uses the meter number.
SELECT '-- Q1 inverter vs billing meter' AS q;
WITH inv AS (
    SELECT plant_id, substr(day, 1, 7) AS month, SUM(inverter_kwh) AS inverter_kwh
    FROM generation_daily GROUP BY plant_id, month
)
SELECT i.plant_id, i.month,
       ROUND(i.inverter_kwh)                                  AS inverter_kwh,
       m.meter_kwh,
       ROUND(100.0 * (i.inverter_kwh - m.meter_kwh) / i.inverter_kwh, 2) AS loss_pct,
       CASE WHEN (i.inverter_kwh - m.meter_kwh) / i.inverter_kwh > 0.03
            THEN 'INVESTIGATE' ELSE 'ok' END                  AS flag
FROM inv i JOIN meter_monthly m USING (plant_id, month)
WHERE (i.inverter_kwh - m.meter_kwh) / i.inverter_kwh > 0.03
   OR i.month IN ('2026-07', '2026-09')                       -- show neighbours for context
ORDER BY i.plant_id, i.month;

-- Q2. Monthly performance ratio (PR) and capacity utilisation factor (CUF).
-- PR = AC energy / (DC kWp x plane-of-array irradiation). Weather-corrected, so it isolates
-- the plant from the sky. CUF = AC energy / (AC kW x hours in month).
SELECT '-- Q2 monthly PR and CUF' AS q;
SELECT g.plant_id, substr(g.day, 1, 7) AS month,
       ROUND(SUM(g.inverter_kwh) / (p.dc_kwp * SUM(r.poa_kwh_m2)), 3) AS pr,
       ROUND(100.0 * SUM(g.inverter_kwh) / (p.ac_kw * 24 * COUNT(*)), 1) AS cuf_pct
FROM generation_daily g
JOIN irradiance_daily r USING (plant_id, day)
JOIN plants p USING (plant_id)
GROUP BY g.plant_id, month
ORDER BY g.plant_id, month;

-- Q3. Which sunny days underperformed, and in runs of how many days?
-- A low-PR day under good irradiation is an equipment problem, not weather.
-- Runs are found with the gaps-and-islands method (day number minus row number).
SELECT '-- Q3 underperformance runs (PR < 0.70 on days with POA >= 4)' AS q;
WITH daily AS (
    SELECT g.plant_id, g.day, r.poa_kwh_m2,
           g.inverter_kwh / (p.dc_kwp * r.poa_kwh_m2) AS pr
    FROM generation_daily g
    JOIN irradiance_daily r USING (plant_id, day)
    JOIN plants p USING (plant_id)
), bad AS (
    SELECT plant_id, day, pr,
           julianday(day) - ROW_NUMBER() OVER (PARTITION BY plant_id ORDER BY day) AS grp
    FROM daily WHERE pr < 0.70 AND poa_kwh_m2 >= 4
)
SELECT plant_id, MIN(day) AS first_day, MAX(day) AS last_day, COUNT(*) AS days,
       ROUND(AVG(pr), 2) AS avg_pr
FROM bad GROUP BY plant_id, grp
HAVING COUNT(*) >= 2
ORDER BY days DESC, first_day;

-- Q4. Is PR drifting down (soiling) and did cleaning restore it?
-- 7-day rolling PR around the April-May window for the ground-mount plant.
SELECT '-- Q4 rolling 7-day PR, ground-mount plant, 20 Apr to 8 May 2026' AS q;
WITH daily AS (
    SELECT g.plant_id, g.day,
           SUM(g.inverter_kwh) OVER w / SUM(p.dc_kwp * r.poa_kwh_m2) OVER w AS pr_7d
    FROM generation_daily g
    JOIN irradiance_daily r USING (plant_id, day)
    JOIN plants p USING (plant_id)
    WINDOW w AS (PARTITION BY g.plant_id ORDER BY g.day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
)
SELECT day, ROUND(pr_7d, 3) AS pr_7d FROM daily
WHERE plant_id = 'PLANT_B' AND day BETWEEN '2026-04-20' AND '2026-05-08'
ORDER BY day;

-- Q5. Revenue billed, and revenue lost to the faults found above.
-- Meter shortfall = inverter energy less a normal 1.5% loss, less what the meter recorded.
-- Downtime loss = what each low-PR sunny day should have produced at the plant's typical PR.
SELECT '-- Q5 annual revenue view' AS q;
WITH daily AS (
    SELECT g.plant_id, g.day, g.inverter_kwh, p.dc_kwp * r.poa_kwh_m2 AS ref_kwh,
           g.inverter_kwh / (p.dc_kwp * r.poa_kwh_m2) AS pr, r.poa_kwh_m2
    FROM generation_daily g
    JOIN irradiance_daily r USING (plant_id, day)
    JOIN plants p USING (plant_id)
), typical AS (
    SELECT plant_id, AVG(pr) AS typical_pr FROM daily WHERE pr >= 0.70 GROUP BY plant_id
), downtime AS (
    SELECT d.plant_id, SUM(d.ref_kwh * t.typical_pr - d.inverter_kwh) AS lost_kwh
    FROM daily d JOIN typical t USING (plant_id)
    WHERE d.pr < 0.70 AND d.poa_kwh_m2 >= 4
    GROUP BY d.plant_id
), inv AS (
    SELECT plant_id, SUM(inverter_kwh) AS inverter_kwh FROM generation_daily GROUP BY plant_id
), met AS (
    SELECT plant_id, SUM(meter_kwh) AS meter_kwh FROM meter_monthly GROUP BY plant_id
)
SELECT p.plant_id, p.tariff_inr_kwh,
       ROUND(m.meter_kwh)                                              AS meter_kwh,
       ROUND(m.meter_kwh * p.tariff_inr_kwh)                           AS billed_inr,
       ROUND((i.inverter_kwh * 0.985 - m.meter_kwh) * p.tariff_inr_kwh) AS meter_shortfall_inr,
       ROUND(COALESCE(dt.lost_kwh, 0) * p.tariff_inr_kwh)              AS downtime_loss_inr
FROM plants p
JOIN inv i USING (plant_id)
JOIN met m USING (plant_id)
LEFT JOIN downtime dt USING (plant_id)
ORDER BY p.plant_id;
