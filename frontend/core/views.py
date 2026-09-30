# core/views.py
# Each function here handles one page — like Express route handlers

import json
import requests
from datetime import datetime

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
            user = form.save()

            Profile.objects.create(
                user=user,
                risk_profile=form.cleaned_data["risk_profile"],
            )

            login(request, user)

            messages.success(
                request,
                "Account created! Welcome."
            )

            return redirect("dashboard")

    else:
        form = RegisterForm()

    return render(
        request,
        "register.html",
        {"form": form}
    )


# ── LOGIN ─────────────────────────────────────────────────────────

def login_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(
            request,
            "Wrong username or password."
        )

    return render(
        request,
        "login.html"
    )


# ── LOGOUT ────────────────────────────────────────────────────────

def logout_view(request):
    logout(request)
    return redirect("home")


# ── DASHBOARD ─────────────────────────────────────────────────────

@login_required
def dashboard(request):

    context = {
        "indices": {},
        "error": None,
        "analysis": None,
        "tips": [],
        "chart_labels": "[]",
        "chart_prices": "[]",
        "market_updated_at": None,
    }

    # -------------------------------------------------
    # Get user's risk profile
    # -------------------------------------------------

    try:
        risk = request.user.profile.risk_profile
    except Exception:
        risk = "moderate"

    context["risk"] = risk

    # -------------------------------------------------
    # Market indices
    # -------------------------------------------------

    try:

        r = requests.get(
            f"{settings.FASTAPI_URL}/stocks/indices",
            timeout=8
        )

        if r.status_code == 200:

            context["indices"] = r.json()

            # Time when Django successfully fetched
            # the market data from the FastAPI backend.
            context["market_updated_at"] = (
                datetime.now().strftime(
                    "%d %b %Y, %I:%M %p"
                )
            )

        else:

            context["error"] = (
                "Market data could not be retrieved."
            )

    except Exception:

        context["error"] = (
            "Market data not available. "
            "Is the FastAPI backend running on port 9000?"
        )

    # -------------------------------------------------
    # Stock search
    # -------------------------------------------------

    symbol = request.GET.get(
        "symbol",
        ""
    ).strip().upper()

    if symbol:

        context["searched"] = symbol

        try:

            # Get stock analysis from FastAPI
            ar = requests.get(
                f"{settings.FASTAPI_URL}/analysis/{symbol}",
                timeout=20
            )

            if ar.status_code == 200:

                data = ar.json()

                # -------------------------------------------------
                # Chart data
                # -------------------------------------------------

                chart = data.get(
                    "chart_data",
                    []
                )

                context["chart_labels"] = json.dumps(
                    [c["date"] for c in chart]
                )

                context["chart_prices"] = json.dumps(
                    [c["close"] for c in chart]
                )

                # -------------------------------------------------
                # Personalised tips
                # -------------------------------------------------

                tr = requests.get(
                    f"{settings.FASTAPI_URL}/analysis/{symbol}/tips",
                    params={"risk": risk},
                    timeout=20
                )

                tips = []

                if tr.status_code == 200:
                    tips = tr.json()

                # -------------------------------------------------
                # Send everything to stock analysis page
                # -------------------------------------------------

                context["analysis"] = data
                context["tips"] = tips

                return render(
                    request,
                    "stock_analysis.html",
                    context
                )

            else:

                context["stock_error"] = (
                    f"No data for '{symbol}'. "
                    "Try a valid NSE symbol like "
                    "RELIANCE or TCS."
                )

        except Exception:

            context["stock_error"] = (
                "Could not reach the market backend "
                "for this stock."
            )

    # -------------------------------------------------
    # Normal dashboard page
    # -------------------------------------------------

    return render(
        request,
        "dashboard.html",
        context
    )


# ── STOCK ANALYSIS ────────────────────────────────────────────────

@login_required
def stock_analysis(request):

    context = {
        "analysis": None,
        "tips": [],
        "risk": "moderate",
        "chart_labels": "[]",
        "chart_prices": "[]",
        "backtest": None,
        "backtest_error": None,
    }

    # -------------------------------------------------
    # Get user's risk profile
    # -------------------------------------------------

    try:
        risk = request.user.profile.risk_profile
    except Exception:
        risk = "moderate"

    context["risk"] = risk

    # -------------------------------------------------
    # Get requested stock
    # -------------------------------------------------

    symbol = request.GET.get(
        "symbol",
        ""
    ).strip().upper()

    if not symbol:

        context["stock_error"] = (
            "Please enter a stock symbol."
        )

        return render(
            request,
            "stock_analysis.html",
            context
        )

    try:

        # -------------------------------------------------
        # Main stock analysis
        # -------------------------------------------------

        ar = requests.get(
            f"{settings.FASTAPI_URL}/analysis/{symbol}",
            params={"risk": risk},
            timeout=30
        )

        if ar.status_code != 200:

            context["stock_error"] = (
                f"No data available for '{symbol}'. "
                "Try RELIANCE, TCS, INFY, HDFCBANK or SBIN."
            )

            return render(
                request,
                "stock_analysis.html",
                context
            )

        data = ar.json()

        context["analysis"] = data
        context["searched"] = symbol

        # -------------------------------------------------
        # Chart data
        # -------------------------------------------------

        chart = data.get(
            "chart_data",
            []
        )

        context["chart_labels"] = json.dumps(
            [c["date"] for c in chart]
        )

        context["chart_prices"] = json.dumps(
            [c["close"] for c in chart]
        )

        # -------------------------------------------------
        # Risk-aware tips
        # -------------------------------------------------

        tr = requests.get(
            f"{settings.FASTAPI_URL}/analysis/{symbol}/tips",
            params={"risk": risk},
            timeout=20
        )

        if tr.status_code == 200:
            context["tips"] = tr.json()

        # -------------------------------------------------
        # Historical backtesting
        # -------------------------------------------------

        br = requests.get(
            f"{settings.FASTAPI_URL}/backtest/{symbol}",
            timeout=60
        )

        if br.status_code == 200:

            backtest_data = br.json()

            if backtest_data.get("success"):

                context["backtest"] = backtest_data

            else:

                context["backtest_error"] = (
                    backtest_data.get(
                        "error",
                        "Backtest data is unavailable."
                    )
                )

        else:

            context["backtest_error"] = (
                "Could not retrieve backtesting results."
            )

    except Exception:

        context["stock_error"] = (
            "Could not reach the market backend for this stock."
        )

    return render(
        request,
        "stock_analysis.html",
        context
    )


# ── VALIDATION ────────────────────────────────────────────────────

@login_required
def validation_dashboard(request):

    context = {
        "validation": None,
        "validation_error": None,
    }

    try:

        response = requests.get(
            f"{settings.FASTAPI_URL}/validation",
            timeout=120
        )

        if response.status_code == 200:

            data = response.json()

            context["validation"] = data

        else:

            context["validation_error"] = (
                "Could not retrieve validation results."
            )

    except Exception as e:

        context["validation_error"] = (
            f"Validation service unavailable: {e}"
        )

    return render(
        request,
        "validation.html",
        context
    )

