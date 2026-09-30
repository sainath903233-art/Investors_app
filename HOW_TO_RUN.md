# Investors_app — How to Run (Complete Web Application)

This project has TWO parts that run at the same time:

- **backend/**  = FastAPI (market data + analysis engine) — runs on port **9000**
- **frontend/** = Django (the website you see) — runs on port **8000**

You will open **two terminals**, one for each part.

---

## ONE-TIME SETUP

### Part A — The Backend (FastAPI)

1. Install PostgreSQL (https://www.postgresql.org/download/) and create the database:
   ```
   psql -U postgres
   ```
   Then inside psql, run:
   ```sql
   CREATE DATABASE investsmart;
   CREATE USER investuser WITH PASSWORD 'mypassword123';
   GRANT ALL PRIVILEGES ON DATABASE investsmart TO investuser;
   \q
   ```

2. Open a terminal in the `backend` folder:
   ```
   cd backend
   python -m venv venv
   venv\Scripts\activate            (Windows)
   # source venv/bin/activate       (Mac/Linux)
   pip install -r requirements.txt
   ```

3. Create your `.env` file. Copy `.env.example` to `.env`:
   ```
   copy .env.example .env           (Windows)
   # cp .env.example .env           (Mac/Linux)
   ```
   The default values already match the database you just created, so you can leave them.

### Part B — The Frontend (Django)

Open a SECOND terminal in the `frontend` folder:
```
cd frontend
python -m venv venv
venv\Scripts\activate               (Windows)
# source venv/bin/activate          (Mac/Linux)
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
The last command asks for a username, email and password — these are your
Admin Page login. Remember them.

---

## RUNNING THE APP (every time)

### Terminal 1 — start the backend on port 9000
```
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 9000
```
Leave it running. (Check it works: open http://localhost:9000/docs)

### Terminal 2 — start the website on port 8000
```
cd frontend
venv\Scripts\activate
python manage.py runserver
```

Now open your browser to **http://localhost:8000/**

---

## THE PAGES

| Page | Address |
|------|---------|
| Home | http://localhost:8000/ |
| About | http://localhost:8000/about/ |
| Features | http://localhost:8000/features/ |
| Contacts | http://localhost:8000/contact/ |
| Help | http://localhost:8000/help/ |
| Register | http://localhost:8000/register/ |
| Login | http://localhost:8000/login/ |
| Dashboard | http://localhost:8000/dashboard/ (after login) |
| Admin Page | http://localhost:8000/admin/ (use your superuser login) |

The **Navbar** (top of every page) has About, Features, Contacts, Help,
and the **Light / Dark theme button**.

---

## HOW TO USE IT

1. Open the site → click **Sign Up** → create an account (pick a risk level).
2. You land on the **Dashboard**. You'll see the live market indices.
3. In the search box, type a stock symbol like **RELIANCE** or **TCS** → click **Analyse**.
4. You'll see the company health score, market timing signal, next-week outlook,
   a small price chart, key insights, and safety tips shaped by your risk level.

---

## IF SOMETHING DOESN'T WORK

- **Dashboard says "Market data not available"** → the backend isn't running.
  Start Terminal 1 (uvicorn on port 9000).
- **Backend error "DATABASE_URL is None"** → your `.env` file is missing in the
  `backend` folder, or its values are wrong.
- **"No data for SYMBOL"** → use a real NSE symbol in capitals (RELIANCE, TCS, INFY…).
  Some small companies don't have all data — that's normal.
- **Port already in use** → close old terminals, or change the port number.

---

## IMPORTANT NOTE

This app is for **educational purposes only**. It is not financial advice.
Always take your own decisions and consult a registered adviser before investing.
