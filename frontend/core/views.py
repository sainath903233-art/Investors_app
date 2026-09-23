# core/views.py
# Each function here handles one page — like Express route handlers

import json
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile


# ── PUBLIC PAGES ──────────────────────────────────────────────────
def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def features(request):
    return render(request, "features.html")

def contact(request):
    return render(request, "contact.html")

def help_page(request):
    return render(request, "help.html")


# ── REGISTER ──────────────────────────────────────────────────────
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()                         # password auto-hashed
            Profile.objects.create(
                user=user,
                risk_profile=form.cleaned_data["risk_profile"],
            )
            login(request, user)                       # log them in right away
            messages.success(request, "Account created! Welcome.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


# ── LOGIN ─────────────────────────────────────────────────────────
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Wrong username or password.")
    return render(request, "login.html")


# ── LOGOUT ────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect("home")


# ── DASHBOARD (only for logged-in users) ──────────────────────────
@login_required
def dashboard(request):
    context = {"indices": {}, "error": None, "analysis": None,
               "tips": [], "chart_labels": "[]", "chart_prices": "[]"}

    # Get the user's risk profile (default moderate if missing)
    try:
        risk = request.user.profile.risk_profile
    except Exception:
        risk = "moderate"
    context["risk"] = risk

    # 1) Live market indices from FastAPI
    try:
        r = requests.get(f"{settings.FASTAPI_URL}/stocks/indices", timeout=8)
        if r.status_code == 200:
            context["indices"] = r.json()
    except Exception:
        context["error"] = "Market data not available. Is the FastAPI backend running on port 9000?"

    # 2) If the user searched a stock, fetch its full analysis
    symbol = request.GET.get("symbol", "").strip().upper()
    if symbol:
        context["searched"] = symbol
        try:
            ar = requests.get(f"{settings.FASTAPI_URL}/analysis/{symbol}", timeout=20)
            if ar.status_code == 200:
                data = ar.json()
                context["analysis"] = data
                # Prepare chart data (dates + closing prices) for the graph
                chart = data.get("chart_data", [])
                context["chart_labels"] = json.dumps([c["date"] for c in chart])
                context["chart_prices"] = json.dumps([c["close"] for c in chart])
                # Get personalised tips
                tr = requests.get(
                    f"{settings.FASTAPI_URL}/analysis/{symbol}/tips",
                    params={"risk": risk}, timeout=20,
                )
                if tr.status_code == 200:
                    context["tips"] = tr.json()
            else:
                context["stock_error"] = f"No data for '{symbol}'. Try a valid NSE symbol like RELIANCE or TCS."
        except Exception:
            context["stock_error"] = "Could not reach the market backend for this stock."

    return render(request, "dashboard.html", context)
