# backend/main.py
# The main FastAPI app — like server.js + routes/ in Express

import sys, os
sys.path.insert(0, os.path.dirname(__file__))   # so Python finds our modules

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import auth as auth_module
import stocks as stocks_module
from analysis.predictor import get_full_analysis
from tips import generate_tips

# Create DB tables on startup (like sequelize.sync())
Base.metadata.create_all(bind=engine)

app = FastAPI(title="InvestSmart API", version="1.0")

# Allow the Django site to call this API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    stocks_module.start_scheduler()   # begin refreshing market data every 2 min


# ── Auth routes (optional — Django has its own login too) ─────────
@app.post("/auth/register")
def register(data: auth_module.UserCreate, db: Session = Depends(get_db)):
    user = auth_module.register_user(data, db)
    return {"id": user.id, "full_name": user.full_name, "email": user.email}

@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_module.login_user(form.username, form.password, db)


# ── Stock data routes (open — no login needed) ────────────────────
@app.get("/stocks/indices")
def get_indices():
    return stocks_module.get_cached_indices()

@app.get("/stocks/{symbol}")
def get_stock(symbol: str):
    data = stocks_module.get_stock_data(symbol.upper())
    if not data:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found.")
    return data


# ── Analysis routes (open, so the Django site can use them) ───────
@app.get("/analysis/{symbol}")
def analyse_stock(symbol: str):
    result = get_full_analysis(symbol.upper())
    if not result:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}.")
    return result

@app.get("/analysis/{symbol}/tips")
def get_tips(symbol: str, risk: str = "moderate"):
    # 'risk' comes from the URL like /analysis/TCS/tips?risk=aggressive
    analysis = get_full_analysis(symbol.upper())
    if not analysis:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}.")
    return generate_tips(analysis, risk)


@app.get("/health")
def health():
    return {"status": "ok"}
