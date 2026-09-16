from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "powerbi" / "data" / "restaurant_pos_powerbi.csv"
RESULTS_DIR = PROJECT_ROOT / "sql" / "results"


QUERIES = {
    "revenue_by_category": """
        SELECT
            category,
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(*) AS pos_records,
            ROUND(AVG(revenue), 2) AS average_line_revenue,
            ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM pos), 2) AS revenue_share_pct
        FROM pos
        GROUP BY category
        ORDER BY total_revenue DESC;
    """,
    "top_menu_items": """
        SELECT
            menu_item,
            category,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(SUM(quantity), 1) AS units_sold,
            COUNT(*) AS pos_records,
            ROUND(AVG(revenue), 2) AS average_line_revenue
        FROM pos
        GROUP BY menu_item, category
        ORDER BY total_revenue DESC
        LIMIT 10;
    """,
    "average_daily_revenue_by_weekday": """
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
    """,
    "revenue_by_hour": """
        SELECT
            hour,
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(*) AS pos_records,
            ROUND(AVG(revenue), 2) AS average_line_revenue
        FROM pos
        GROUP BY hour
        ORDER BY total_revenue DESC;
    """,
    "server_performance": """
        SELECT
            server_name,
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(*) AS pos_records,
            ROUND(SUM(quantity), 1) AS units_sold,
            ROUND(AVG(revenue), 2) AS average_line_revenue,
            ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM pos), 2) AS revenue_share_pct
        FROM pos
        GROUP BY server_name
        ORDER BY total_revenue DESC;
    """,
    "dessert_upsell_by_server": """
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
    """,
}


def run_sql_analysis() -> None:
    df = pd.read_csv(DATA_PATH)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(":memory:") as connection:
        df.to_sql("pos", connection, index=False, if_exists="replace")

        for query_name, query in QUERIES.items():
            result = pd.read_sql_query(query, connection)
            output_path = RESULTS_DIR / f"{query_name}.csv"
            result.to_csv(output_path, index=False)
            print(f"Exported {output_path}")


if __name__ == "__main__":
    run_sql_analysis()
