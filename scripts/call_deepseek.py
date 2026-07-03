import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def call_gemini(yields, history_df):
    """Call Gemini with last 365 days of full macro data and return expanded AI analysis."""
    if not GEMINI_API_KEY:
        return "⚠️ No API key. Please set GEMINI_API_KEY."

    # Process historical data context
    if history_df is not None and len(history_df) > 0:
        history_df = history_df.sort_values("date")
        last_365 = history_df.tail(365)
        yield_history = last_365.to_string(index=False)
        latest_macro = history_df.iloc[-1]
    else:
        yield_history = "No historical data available."
        latest_macro = {}

    # Calculate all 4 spreads
    s30_2 = yields.get('30Y', 0) - yields.get('2Y', 0)
    s10_2 = yields.get('10Y', 0) - yields.get('2Y', 0)
    s10_3 = yields.get('10Y', 0) - yields.get('3M', 0)
    s30_5 = yields.get('30Y', 0) - yields.get('5Y', 0)
    
    dxy = yields.get('DXY')
    fedfunds = yields.get('FEDFUNDS')
    dxy_str = f"{dxy:.2f}" if dxy else "N/A"
    fed_str = f"{fedfunds:.2f}" if fedfunds else "N/A"

    # Helper to safely format macro data if it exists
    def fmt(val): 
        return f"{val:.3f}" if pd.notnull(val) else "N/A"

    # Compile the new macro snapshot for the prompt
    macro_snapshot = f"""
    M2 Money Supply (Trillions): {fmt(latest_macro.get('M2SL'))}
    Fed Balance Sheet - WALCL (Trillions): {fmt(latest_macro.get('WALCL'))}
    GDP (Trillions): {fmt(latest_macro.get('GDP'))}
    Federal Debt (Trillions): {fmt(latest_macro.get('GFDEBTN'))}
    CPI (AUCSL): {fmt(latest_macro.get('CPIAUCSL'))}
    PPI (ACO): {fmt(latest_macro.get('PPIACO'))}
    Avg Hourly Earnings: {fmt(latest_macro.get('AHE'))}
    Unemployment Rate: {fmt(latest_macro.get('UNRATE'))}%
    Nonfarm Payrolls (Millions): {fmt(latest_macro.get('PAYEMS'))}
    Job Openings (Millions): {fmt(latest_macro.get('JTSJOL'))}
    Housing Supply (Months): {fmt(latest_macro.get('HOSINV'))}
    """
    
    prompt = f"""
You are a top-tier macro strategist. Analyze the US Treasury yield curve and the comprehensive macroeconomic data using the dataset below.

Last 365 days of yields and macro data:
{yield_history}

Current Yields Snapshot: 
3M={yields.get('3M', 0):.2f}%, 2Y={yields.get('2Y', 0):.2f}%, 5Y={yields.get('5Y', 0):.2f}%, 10Y={yields.get('10Y', 0):.2f}%, 30Y={yields.get('30Y', 0):.2f}%
Spreads: 30Y-2Y={s30_2:.2f}%, 10Y-2Y={s10_2:.2f}%, 10Y-3M={s10_3:.2f}%, 30Y-5Y={s30_5:.2f}%
US Dollar Index (DXY): {dxy_str}
Fed Funds Rate: {fed_str}%

Current Macroeconomic Snapshot (Latest Available):
{macro_snapshot}

Provide a complete, vivid, and highly authentic 360° analysis backed by the data.
For your analysis, you MUST:
- Explicitly calculate and analyze the Week-over-Week (WoW), Month-over-Month (MoM), and Year-over-Year (YoY) changes for the spreads, yields, and macro datasets (inflation, employment, liquidity, debt) based on the 365-day history provided.
- Include the rationale/mechanism behind every prediction (why, not just what).
- Detail how global money flows and liquidity (M2/WALCL) are moving and impacting asset prices.
- Use varied, institutional vocabulary.

Do NOT include:
- Any explanation of economic jargon (no footnotes, no definitions).
- Duplicate display of yields or spreads.

Structure your response exactly as follows:

1. MACROECONOMIC & LIQUIDITY TRENDS
   Detailed breakdown of WoW, MoM, and YoY changes in the provided macro data (CPI, PPI, M2, WALCL, Jobs, Debt, Housing). Analyze the current macro regime based on these shifts.

2. YIELD OUTLOOK (Short/Medium/Long)
   For each tenor and key spread, state the direction, historical trend (WoW/MoM/YoY), and rationale. Reference historical parallels.

3. EQUITIES
   Preferred/avoid sectors + regions with rationale. Mention valuation mechanics relative to the liquidity and employment data.

4. BONDS
   Preferred/avoid duration + credit quality. Explain why each is favored or avoided.

5. GOLD & PRECIOUS METALS
   Direction and rationale. Compare gold vs silver in the context of the current DXY, CPI, and Fed Balance Sheet trends.

6. COMMODITIES
   Energy, metals, agriculture – outlook and drivers relative to PPI and global flows.

7. CASH & FX
   USD direction and key FX pairs. Explain yield differentials and safe-haven flows.

8. PORTFOLIO MIX & ACTIONABLE STRATEGY
   a. Suggested allocation % (Equity, Bonds, Gold, Silver, Bitcoin, Cash)
   b. Preferred equity theme and why
   c. Avoid equity theme and why
   d. Preferred bond duration and why
   e. Avoid bond duration and why
   f. Gold vs Silver vs Bitcoin – which one and why
   g. Global money flow trend – where capital is moving

9. SCENARIO ANALYSIS
   Provide 2–3 plausible future scenarios (Base, Bull, Bear) for yields and markets over the next 12 months.
   For each scenario, explicitly state:
   - The specific future outlook
   - The underlying rationale and macro triggers
   - The precise probability of this outcome occurring

Keep the analysis exhaustive, highly analytical, and forward-looking. Maximize output quality.
"""
    headers = {"Content-Type": "application/json"}
    
    # Models array kept identical to original script
    models_to_try = ["gemini-2.5-pro", "gemini-3.5-flash", "gemini-2.5-flash"]
    
    for model in models_to_try:
        print(f"🔄 Trying model: {model}...")
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 8192, # Ensured maximum generation length
                "temperature": 0.7,
                "topP": 0.95
            }
        }
        
        try:
            response = requests.post(f"{api_url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    if "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"]:
                        text = result["candidates"][0]["content"]["parts"][0]["text"]
                        if text and len(text.strip()) > 0:
                            print(f"✅ Success with model: {model}")
                            return text
                        else:
                            print(f"⚠️ Model {model} returned empty text")
                    else:
                        print(f"⚠️ Model {model} returned invalid structure")
                else:
                    print(f"⚠️ Model {model} returned no candidates")
            else:
                print(f"⚠️ Model {model} failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"⚠️ Model {model} error: {e}")
    
    return "⚠️ All Gemini models failed to generate analysis. Please check API key or try again later."


def generate_daily_report(yields, regime, confidence, explanation, history_df):
    """Generate full report with AI analysis. (Data presentation structure unchanged)"""
    analysis = call_gemini(yields, history_df)

    s30_2 = yields.get('30Y', 0) - yields.get('2Y', 0)
    s10_2 = yields.get('10Y', 0) - yields.get('2Y', 0)
    s10_3 = yields.get('10Y', 0) - yields.get('3M', 0)
    s30_5 = yields.get('30Y', 0) - yields.get('5Y', 0)

    return f"""
============================================================
📅 YIELD CURVE DAILY REPORT - {yields['date']}
============================================================

📊 YIELD DATA:
  3M: {yields.get('3M', 0):.2f}%   2Y: {yields.get('2Y', 0):.2f}%   5Y: {yields.get('5Y', 0):.2f}%
  10Y: {yields.get('10Y', 0):.2f}%   30Y: {yields.get('30Y', 0):.2f}%

📈 SPREADS:
  30Y-2Y (Liquidity): {s30_2:.2f}%
  10Y-2Y (Risk):      {s10_2:.2f}%
  10Y-3M (Recession): {s10_3:.2f}%
  30Y-5Y (Long-Term): {s30_5:.2f}%

🔍 REGIME: {regime} (Confidence: {confidence:.2f})
  {explanation}

📋 AI ANALYSIS:
{analysis}
============================================================
✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Gemini
"""
