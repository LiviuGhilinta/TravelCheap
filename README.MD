# TravelCheap

TravelCheap is a desktop application that helps users find and compare the cheapest flight tickets and see the weather forecast for their chosen destination and travel dates, all in one place.

## Features

- Search for **one-way** and **round-trip** flights
- Airport autocomplete backed by a local **SQLite** database
- Date selection with a calendar (past dates are corrected, and the return date can never be before the departure date)
- Results for the cheapest low-cost flights, with price, duration, schedule, class and a **direct link to the airline's booking page**
- **Weather forecast** for the first 3 days of the selected period
- Responsive UI: flight and weather requests run **in parallel on a background thread**, so the window never freezes
- Result caching: repeating the same search does not call the APIs again

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3.13 |
| GUI | PyQt5 |
| Data | SQLite (airports), JSON |
| APIs | [SerpAPI](https://serpapi.com/) (flights), [Visual Crossing Weather](https://www.visualcrossing.com/) (weather) |
| Libraries | `requests`, `python-dotenv`, `datetime`, `sqlite3`, `concurrent.futures` |
| Testing | pytest, pytest-qt |
| CI/CD | Jenkins (Build → Test → Deploy) |
| Containers | Docker |
| Editor | Visual Studio Code |

## Project Structure

```
TravelCheap/
├── src/
│   ├── Airport_Search.py   # main application and UI
│   ├── Flights.py          # flight search (SerpAPI)
│   ├── Weather.py          # weather forecast (Visual Crossing)
│   └── IMG/                # images and backgrounds
├── test/
│   └── test_ui.py          # pytest UI and logic tests
├── Airports.db             # SQLite database (city, IATA code)
├── Dockerfile
├── Jenkinsfile
├── pytest.ini
├── requirements.txt
└── .env                    # API keys (not committed)
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/TravelCheap.git
cd TravelCheap
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS
pip install -r requirements.txt
```

### 3. Configure API keys

Create a `.env` file in the project root (this file is git-ignored):

```env
SERPAPI_KEY=your_serpapi_key
WEATHER_KEY=your_visual_crossing_key
```

> Use the variable names expected in `Flights.py` and `Weather.py`.

### 4. Run the application

```bash
python src/Airport_Search.py
```

## Usage

1. Run `Airport_Search.py`.
2. Click **Let's Start**.
3. Select the flight type (one-way / round-trip).
4. Choose the departure and arrival airports and the travel dates using the calendar.
5. Set the number of adults and click **Search**.
6. On the next page you will find the cheapest low-cost flights, with price and flight details and a direct link to the booking page.
7. At the bottom, the weather forecast for the first 3 days of the selected period is displayed.
8. Use the **X** button, available on every page, to close the application.


👤 Author Liviu Ghilință

GitHub: @LiviuGhilinta
