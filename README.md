# Placement Application Tracker

A Streamlit app for tracking job applications in a local SQLite database.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
streamlit run app.py
```

Application data is stored in `placements.db`, which is intentionally excluded from Git.
