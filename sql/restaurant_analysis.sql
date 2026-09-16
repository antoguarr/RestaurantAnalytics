-- Restaurant POS SQL Analysis
-- These queries are written for SQLite and run against the cleaned
-- Power BI export table named pos.

-- 1. Revenue by menu category
SELECT
    category,
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(*) AS transactions,
    ROUND(AVG(revenue), 2) AS average_order_value,
    ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM pos), 2) AS revenue_share_pct
FROM pos
GROUP BY category
ORDER BY total_revenue DESC;

-- 2. Top menu items by revenue
SELECT
    menu_item,
    category,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(quantity), 1) AS units_sold,
    COUNT(*) AS transactions,
    ROUND(AVG(revenue), 2) AS average_order_value
FROM pos
GROUP BY menu_item, category
ORDER BY total_revenue DESC
LIMIT 10;

-- 3. Average daily revenue by weekday
WITH daily_revenue AS (
    SELECT
        date,
        weekday,
        day_of_week,
        SUM(revenue) AS daily_revenue
    FROM pos
    GROUP BY date, weekday, day_of_week
)
SELECT
    weekday,
    ROUND(AVG(daily_revenue), 2) AS average_daily_revenue,
    ROUND(SUM(daily_revenue), 2) AS total_revenue,
    COUNT(*) AS days_observed
FROM daily_revenue
GROUP BY weekday, day_of_week
ORDER BY day_of_week;

-- 4. Revenue by hour
SELECT
    hour,
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(*) AS transactions,
    ROUND(AVG(revenue), 2) AS average_order_value
FROM pos
GROUP BY hour
ORDER BY total_revenue DESC;

-- 5. Server performance
SELECT
    server_name,
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(*) AS transactions,
    ROUND(SUM(quantity), 1) AS units_sold,
    ROUND(AVG(revenue), 2) AS average_order_value,
    ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM pos), 2) AS revenue_share_pct
FROM pos
GROUP BY server_name
ORDER BY total_revenue DESC;

-- 6. Dessert upsell opportunity by server
SELECT
    server_name,
    ROUND(SUM(CASE WHEN category = 'Dessert' THEN revenue ELSE 0 END), 2) AS dessert_revenue,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(
        SUM(CASE WHEN category = 'Dessert' THEN revenue ELSE 0 END) * 100.0 / SUM(revenue),
        2
    ) AS dessert_revenue_share_pct
FROM pos
GROUP BY server_name
ORDER BY dessert_revenue_share_pct DESC;
