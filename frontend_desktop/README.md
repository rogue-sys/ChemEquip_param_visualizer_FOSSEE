# Chemical Equipment Parameter Visualizer — Desktop Client

A PyQt5 desktop application that consumes the Django REST Framework backend.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your backend URL in api.py
#    Edit the BASE_URL constant:
#      BASE_URL = "https://YOUR-BACKEND-URL.onrender.com/api"

# 3. Run the app
python main.py
```

## Project Structure

```
frontend_desktop/
├── main.py         — App entry point; QMainWindow + QStackedWidget routing
├── session.py      — In-memory session state (token, username)
├── api.py          — All HTTP calls to the Django backend
├── login.py        — Login screen widget
├── dashboard.py    — Dashboard (upload CSV, nav to history/logout)
├── summary.py      — Summary stats display + toggle charts
├── history.py      — Upload history list
├── charts.py       — Embedded Matplotlib charts (bar charts)
└── requirements.txt
```

## Architecture

- **Thin client** — no local CSV parsing; all analytics come from backend.
- **Session object** — passed to widgets that need auth; no globals.
- **Background workers** — every network call runs in a QThread so the UI stays responsive.
- **QStackedWidget** — screens are pre-built and swapped instantly.

## Expected User Flow

```
Login → Dashboard → Upload CSV → Summary (+ Charts) → Back → Dashboard
                 ↘ History → click item → Summary → Back → Dashboard
                 ↘ Logout → Login
```
