# backend/analysis/genai.py
# Generative AI explanation layer for InvestSmart

import os
import time

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


# Load variables from backend/.env
load_dotenv()


# Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")


# ---------------------------------------------------------
# Clean AI text
# ---------------------------------------------------------

def clean_ai_text(text: str) -> str:
    """Remove simple Markdown formatting from Gemini output."""

    if not text:
        return ""

    text = text.replace("**", "")
    text = text.replace("__", "")

    return text.strip()


# ---------------------------------------------------------
# Structured response format
# ---------------------------------------------------------

class AIRecommendation(BaseModel):

    explanation: str = Field(
        description=(
            "A clear 2-3 paragraph explanation of the stock analysis."
        )
    )

    key_risks: list[str] = Field(
        description=(
            "Exactly 3 important risks based on the provided analysis."
        )
    )

    what_to_watch: list[str] = Field(
        description=(
            "Exactly 3 things the investor should monitor."
        )
    )

    risk_aware_view: str = Field(
        description=(
            "Explain how the information may be interpreted "
            "for the user's risk profile."
        )
    )


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

def get_genai_client():

    if not API_KEY:
        return None

    return genai.Client(
        api_key=API_KEY
    )


# ---------------------------------------------------------
# Generate AI recommendation
# ---------------------------------------------------------

def generate_ai_recommendation(
    symbol: str,
    name: str,
    risk_profile: str,
    fundamental: dict,
    technical: dict,
    prediction: dict,
) -> dict:

    client = get_genai_client()

    # -----------------------------------------------------
    # API key missing
    # -----------------------------------------------------

    if client is None:

        return {
            "success": False,
            "message": (
                "Gemini API key is not configured."
            ),
            "explanation": "",
            "key_risks": [],
            "what_to_watch": [],
            "risk_aware_view": "",
        }


    # -----------------------------------------------------
    # Prompt
    # -----------------------------------------------------

    prompt = f"""
You are the Generative AI explanation layer of an educational
investment-analysis application called InvestSmart.

Your role is to explain the results produced by a deterministic
Python financial-analysis engine.

You are NOT responsible for calculating financial scores.
The scores are already calculated by the Python engine.

IMPORTANT RULES:

1. Do not invent financial numbers.
2. Only use the information provided below.
3. Do not create statistics that are not provided.
4. Do not claim certainty about future prices.
5. Do not describe score-derived values as probabilities.
6. Do not give guaranteed investment outcomes.
7. Do not tell the user to buy or sell a stock.
8. Consider the investor's risk profile.
9. Clearly distinguish evidence from interpretation.
10. Keep the explanation understandable for a retail investor.
11. This is educational information, not financial advice.
12. Use benchmark values exactly as supplied by the Python engine.
13. Never invent or substitute a sector benchmark.
14. If a benchmark is not provided, say that it is unavailable.
15. Do not change any supplied score, value, weight, or benchmark.
16. Do not calculate financial metrics yourself.

STOCK INFORMATION

Symbol:
{symbol}

Company:
{name}

Investor Risk Profile:
{risk_profile}


FUNDAMENTAL ANALYSIS

Overall Score:
{fundamental.get("overall_score")}

Verdict:
{fundamental.get("verdict")}

Fundamental Metrics:
{fundamental.get("metrics")}

Important:
Use the metric value, score, weight, contribution, note,
and benchmark fields exactly as supplied.


TECHNICAL ANALYSIS

Overall Score:
{technical.get("overall_score")}

Signal:
{technical.get("overall_signal")}

Verdict:
{technical.get("verdict")}

Technical Indicators:
{technical.get("indicators")}


WEEKLY OUTLOOK

Prediction:
{prediction.get("prediction")}

Description:
{prediction.get("description")}

Combined Score:
{prediction.get("combined_score")}


Generate a structured response containing:

EXPLANATION:
Write 2-3 clear paragraphs explaining the major positive
and negative evidence.

KEY RISKS:
Provide exactly 3 concise risks based only on the supplied data.

WHAT TO WATCH:
Provide exactly 3 observable factors that the investor
should monitor.

RISK-AWARE VIEW:
Explain how the same evidence may be interpreted for the
user's specific risk profile.

Do not invent missing information.
"""


    # -----------------------------------------------------
    # Generate structured response
    # -----------------------------------------------------

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
    ]

    response = None
    last_error = None

    for model_name in models_to_try:

        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": AIRecommendation,
                    },
                )

                break

            except Exception as e:

                last_error = e

                if attempt == 0:
                    time.sleep(2)

        if response is not None:
            break


    # -----------------------------------------------------
    # All Gemini attempts failed
    # -----------------------------------------------------

    if response is None:

        return {
            "success": False,
            "message": (
                f"Gemini request failed: {last_error}"
            ),
            "explanation": "",
            "key_risks": [],
            "what_to_watch": [],
            "risk_aware_view": "",
        }


    # -----------------------------------------------------
    # Read structured response
    # -----------------------------------------------------

    try:

        parsed = response.parsed

        if parsed is None:

            return {
                "success": False,
                "message": (
                    "Gemini returned no structured response."
                ),
                "explanation": "",
                "key_risks": [],
                "what_to_watch": [],
                "risk_aware_view": "",
            }


        if isinstance(
            parsed,
            AIRecommendation
        ):

            data = parsed.model_dump()

        else:

            data = dict(parsed)


        # -------------------------------------------------
        # Clean generated text
        # -------------------------------------------------

        explanation = clean_ai_text(
            data.get(
                "explanation",
                ""
            )
        )


        key_risks = [
            clean_ai_text(item)
            for item in data.get(
                "key_risks",
                []
            )
        ]


        what_to_watch = [
            clean_ai_text(item)
            for item in data.get(
                "what_to_watch",
                []
            )
        ]


        risk_aware_view = clean_ai_text(
            data.get(
                "risk_aware_view",
                ""
            )
        )


        # -------------------------------------------------
        # Return successful response
        # -------------------------------------------------

        return {

            "success": True,

            "message": (
                "AI analysis generated successfully."
            ),

            "explanation": explanation,

            "key_risks": key_risks,

            "what_to_watch": what_to_watch,

            "risk_aware_view": risk_aware_view,
        }


    except Exception as e:

        return {

            "success": False,

            "message": (
                f"Gemini response processing failed: {e}"
            ),

            "explanation": "",

            "key_risks": [],

            "what_to_watch": [],

            "risk_aware_view": "",
        }