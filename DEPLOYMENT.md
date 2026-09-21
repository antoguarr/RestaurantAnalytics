# Deployment Guide

## Streamlit Community Cloud

This project is ready for Streamlit Community Cloud deployment.

Use these settings:

```text
Repository: antoguarr/RestaurantAnalytics
Branch: main
Main file path: app.py
Python dependencies: requirements.txt
```

After deployment, copy the live app URL into the top of `README.md`.

## Tableau Public

The Tableau source is ready to publish without exposing private data. The original dataset is public and simulated or highly curated.

1. Sign in to [Tableau Public](https://public.tableau.com/).
2. Select **Create** and upload:

```text
tableau/data/restaurant_pos_tableau.xlsx
```

3. Follow the worksheet and dashboard specification in `tableau/README.md`.
4. Publish as `Restaurant POS Sales Analytics`.
5. Open the public visualization in a signed-out browser window to verify access.
6. Add the public URL near the top of `README.md`.

Tableau Public publishes the workbook and underlying data publicly. Do not use this deployment method for confidential business data.

## GitHub Repository Metadata

Recommended description:

```text
Restaurant POS analytics project with Python, SQL, Streamlit, Tableau, Power BI, and machine learning model evaluation.
```

Recommended topics:

```text
python
pandas
streamlit
plotly
scikit-learn
sql
sqlite
powerbi
tableau
data-analysis
dashboard
machine-learning
restaurant-analytics
```

## Local Verification Before Deploying

Run:

```bash
python scripts/export_powerbi_data.py
python scripts/export_tableau_data.py
python scripts/create_tableau_previews.py
python scripts/run_sql_analysis.py
python scripts/create_readme_screenshots.py
streamlit run app.py
```

Then confirm the dashboard opens locally and all tabs render correctly.
