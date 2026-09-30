# InvestSmart

**Stock Analysis & Investment Advisory System**

InvestSmart is a team-developed full-stack web application that helps users understand stock performance using **fundamental analysis, technical analysis, historical backtesting, and Generative AI-based insights**.

## Features

* 🔐 User registration and login
* 📊 Market index monitoring
* 📈 Stock price charts
* 📋 Fundamental analysis
* 📉 Technical analysis
* 🤖 Generative AI-based stock insights
* 🧪 Historical backtesting
* 🛡️ Risk-based investment tips
* 🔄 Automatic market-data refresh
* 📚 FastAPI Swagger API documentation

## Tech Stack

**Frontend**

* Django
* HTML/CSS/JavaScript
* Chart.js

**Backend**

* FastAPI
* Python
* SQLAlchemy
* APScheduler

**Database**

* PostgreSQL

**Data & AI**

* Yahoo Finance (`yfinance`)
* Pandas
* NumPy
* TA
* Google GenAI

## Architecture

```text
Django Frontend
       ↓
FastAPI Backend
       ↓
 ┌─────┼──────────────┐
 ↓     ↓              ↓
PostgreSQL      Yahoo Finance
                       ↓
                Analysis Engine
                       ↓
                  Google GenAI
```

## Project Structure

```text
Investors_app/
├── backend/
│   ├── main.py
│   ├── stocks.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   └── analysis/
│
├── frontend/
│   ├── manage.py
│   ├── core/
│   ├── templates/
│   └── static/
│
├── .gitignore
└── README.md
```

## Setup

### Backend

```bash
cd backend
py -3.12 -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
python -m uvicorn main:app --port 9000
```

### Frontend

Open another terminal:

```bash
cd frontend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies and run Django:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## URLs

| Service        | URL                          |
| -------------- | ---------------------------- |
| Django Website | `http://127.0.0.1:8000/`     |
| FastAPI        | `http://127.0.0.1:9000/`     |
| Swagger API    | `http://127.0.0.1:9000/docs` |

## Supported Stocks

The application currently supports analysis for stocks including:

* TCS
* RELIANCE
* INFY
* HDFCBANK
* SBIN
* ICICIBANK
* WIPRO
* BAJFINANCE

## Team

This is a **team-developed academic project**. The project was initially developed collaboratively and later continued under the team lead's repository for centralized development and project management.

## Disclaimer

Investors_app is an **educational project**. Its analysis and AI-generated insights are not professional financial advice and should not be used as the sole basis for investment decisions.
