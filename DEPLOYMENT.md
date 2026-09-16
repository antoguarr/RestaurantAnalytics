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

## GitHub Repository Metadata

Recommended description:

```text
Interactive restaurant POS analytics project with Python, SQL, Streamlit, Power BI preparation, and machine learning model evaluation.
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
data-analysis
dashboard
machine-learning
restaurant-analytics
```

## Local Verification Before Deploying

Run:

```bash
python scripts/export_powerbi_data.py
python scripts/run_sql_analysis.py
python scripts/create_readme_screenshots.py
streamlit run app.py
```

Then confirm the dashboard opens locally and all tabs render correctly.
