# ⚗️ Chemical Equipment Parameter Visualizer — Desktop Client

A responsive PyQt5 desktop application that consumes the Django REST Framework backend to visualise and analyse chemical equipment parameters.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your backend URL in api.py
#    Edit the BASE_URL constant (line 11):
BASE_URL = "http://127.0.0.1:8000/api"

# 3. Run the app
python main.py
```

---

## Project Structure

```
frontend_desktop/
├── main.py           — App entry point; QMainWindow + QStackedWidget routing
├── session.py        — In-memory session state (token, username)
├── api.py            — All HTTP calls to the Django backend
├── login.py          — Login screen with show/hide password toggle
├── register.py       — Registration screen with live validation + strength meter
├── dashboard.py      — Dashboard: CSV upload (drag & drop), history, logout
├── summary.py        — Summary stats, distribution table, charts, PDF export
├── history.py        — Upload history list (last 5 datasets)
├── charts.py         — 2×2 embedded Matplotlib chart grid
├── export_pdf.py     — 2-page dark-theme PDF report generator
└── requirements.txt
```

---

## Features

### 🔐 Authentication
- **Login** — Token-based auth via Django REST Framework
- **Register** — New account creation with live username validation, password strength meter, and confirm password check
- **Show / Hide password** — Eye toggle on all password fields
- **Logout confirmation** — Stylish custom dialog asks "Are you sure?" before clearing session

### 📂 Dashboard
- **CSV Upload** — Click to browse or drag & drop a `.csv` file directly onto the drop zone
- **Upload History** — One-click access to the last 5 uploaded datasets

### 📊 Summary & Charts
- **4 stat cards** — Total Equipment, Avg Flowrate, Avg Pressure, Avg Temperature
- **Distribution table** — All equipment types with count and percentage
- **2×2 Chart grid** (toggle on/off):
  - Horizontal bar chart — equipment type distribution with progress tracks
  - Donut chart — equipment share with percentage legend
  - Arc gauges — semi-circle gauges for each average metric
  - Vertical bar chart — styled metric comparison bars

### 📄 PDF Export
- **Export PDF** button on the Summary screen
- Generates a **2-page dark-theme PDF report**:
  - Page 1 — Cover page with stat cards, distribution table and progress bars
  - Page 2 — All 4 charts at print quality
- Includes report metadata (title, author, creation date)
- Save dialog lets you choose the output location

### 🕒 History
- Lists the last 5 uploads for the logged-in user
- Click any item to view its full summary and charts
- Backend enforces per-user data isolation

---

## Architecture

| Principle | Detail |
|---|---|
| **Thin client** | Zero local CSV parsing — all analytics come from the backend |
| **Session object** | `Session` class passed by reference; no globals |
| **QThread workers** | Every network call runs off the main thread — UI never freezes |
| **QStackedWidget** | All 5 screens pre-built and swapped instantly, no re-renders |
| **Responsive layout** | `setMaximumWidth` + `QSizePolicy.Expanding` on all pages; outer `QScrollArea` handles small windows |

---

## API Endpoints Used

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/login/` | Authenticate user, receive token |
| `POST` | `/api/register/` | Create new user account |
| `POST` | `/api/upload/` | Upload CSV, receive summary JSON |
| `GET`  | `/api/history/` | Fetch last 5 upload records |

All authenticated requests send `Authorization: Token <token>` header.

---

## Summary JSON Keys Expected

```json
{
  "total_count": 15,
  "avg_flowrate": 119.8,
  "avg_pressure": 6.11,
  "avg_temperature": 117.47,
  "type_distribution": {
    "Pump": 4,
    "Valve": 3,
    "Compressor": 2,
    ...
  }
}
```

---

## Dependencies

```
PyQt5>=5.15.0
requests>=2.28.0
matplotlib>=3.6.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## User Flow

```
Open App
  │
  ├─ New user?  → Register → auto-login → Dashboard
  │
  └─ Existing?  → Login ──────────────→ Dashboard
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                         Upload CSV    View History    Logout (confirm)
                              │             │
                              ▼             ▼
                           Summary ◄── click item
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
               View Charts          Export PDF
```