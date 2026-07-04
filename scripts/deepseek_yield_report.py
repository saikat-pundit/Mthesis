import os
import sys
from datetime import datetime
import pandas as pd
from openai import OpenAI
from dateutil.relativedelta import relativedelta

def main():
    print("🚀 Starting parallel DeepSeek-v4-Pro yield report...")
    
    # 1. Setup API Client
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    if not NVIDIA_API_KEY:
        print("⚠️ No NVIDIA_API_KEY found. Check GitHub Secrets.")
        return

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=NVIDIA_API_KEY
    )

    # 2. Load and prep data
    csv_file = "data/yield_history.csv"
    if not os.path.exists(csv_file):
        print(f"⚠️ {csv_file} not found.")
        return

    df = pd.read_csv(csv_file)
    if df.empty:
        return
        
    df['date'] = pd.to_datetime(df['date'])
    latest_date = df['date'].iloc[-1]
    date_str = latest_date.strftime('%Y-%m-%d')

    # 3. Smart Historical Calculator (Handles Daily, Monthly, and Quarterly data)
    def get_historical_metric(col, is_rate=False):
        if col not in df.columns:
            return f"{col}: N/A"
        valid_df = df[['date', col]].dropna()
        if valid_df.empty:
            return f"{col}: N/A"
            
        curr_val = valid_df[col].iloc[-1]
        
        # Helper to find closest date looking backwards
        def get_val_at(months_back):
            target_date = latest_date - relativedelta(months=months_back)
            # Find the closest valid data point on or before the target date
            past_df = valid_df[valid_df['date'] <= target_date]
            if not past_df.empty:
                return past_df[col].iloc[-1]
            return None

        val_1m = get_val_at(1)
        val_1q = get_val_at(3)
        val_1y = get_val_at(12)
        val_2y = get_val_at(24)
        
        def calc_change(past_val):
            if past_val is None or past_val == 0: return "N/A"
            if is_rate:
                bps = (curr_val - past_val) * 100
                return f"{'+' if bps > 0 else ''}{bps:.0f} bps"
            else:
                pct = ((curr_val - past_val) / past_val) * 100
                return f"{'+' if pct > 0 else ''}{pct:.2f}%"

        return f"Current: {curr_val:.2f} | MoM: {calc_change(val_1m)} | QoQ: {calc_change(val_1q)} | YoY: {calc_change(val_1y)} | 2-Year: {calc_change(val_2y)}"

    # 4. Generate Pre-Calculated Growth Metrics
    macro_trends = f"""
    --- 2-YEAR GROWTH & RATE TRAJECTORIES (MoM, QoQ, YoY, 2-Year) ---
    
    YIELDS & RATES (Changes in Basis Points):
    3M Yield: {get_historical_metric('3M', is_rate=True)}
    2Y Yield: {get_historical_metric('2Y', is_rate=True)}
    10Y Yield: {get_historical_metric('10Y', is_rate=True)}
    30Y Yield: {get_historical_metric('30Y', is_rate=True)}
    Fed Funds Rate: {get_historical_metric('FEDFUNDS', is_rate=True)}
    
    MACRO ECONOMY (Changes in Percentages):
    GDP (Trillions): {get_historical_metric('GDP')}
    Federal Debt (Trillions): {get_historical_metric('GFDEBTN')}
    CPI Inflation Index: {get_historical_metric('CPIAUCSL')}
    PPI Inflation Index: {get_historical_metric('PPIACO')}
    US Dollar Index (DXY): {get_historical_metric('DXY')}
    
    LABOR, WAGES, & HOUSING (Changes in Percentages):
    Unemployment Rate: {get_historical_metric('UNRATE', is_rate=True)}
    Nonfarm Payrolls: {get_historical_metric('PAYEMS')}
    Average Hourly Earnings (Wages): {get_historical_metric('AHE')}
    Housing Supply (Months): {get_historical_metric('HOSINV')}
    
    LIQUIDITY (Changes in Percentages):
    M2 Money Supply: {get_historical_metric('M2SL')}
    Fed Balance Sheet (WALCL): {get_historical_metric('WALCL')}
    """

    # Extract exactly 2 years of raw historical data
    two_years_ago = latest_date - relativedelta(years=2)
    df_last_2_years = df[df['date'] >= two_years_ago]
    raw_2y_data_str = df_last_2_years.to_string(index=False)

    # 5. The Highly Constrained Prompt
    prompt = f"""
    You are a top-tier macro strategist. I have pre-calculated the exact growth trajectories (MoM, QoQ, YoY, 2-Year) for the US economy, bond yields, and labor market, AND I am providing the raw 2-year timeline.
    
    DATA TRAJECTORIES:
    {macro_trends}

    RAW 2-YEAR HISTORICAL DATA:
    {raw_2y_data_str}

    Your mandate is to provide a complete, vivid, and highly authentic 360° analysis.

    STRICT RULES FOR YOUR OUTPUT:
    1. NO RAW DATA DUMPING: Never just list out numbers or say "CPI is at X". You must WEAVE the growth percentages and basis point changes naturally into your sentences to prove a trend.
    2. ASSET CLASS PREFERENCES (CRITICAL): For Equities, Bonds, Gold, Commodities, and FX, you MUST explicitly state what to "PREFER" (e.g., sectors, specific bond tenors, specific currencies) and what to "AVOID". Every preference/avoidance MUST be immediately justified using the provided growth/inflation/liquidity data.
    3. THE HUMAN ANGLE (Crucial): You MUST dedicate analysis to how the "Main Street" human is faring. Explicitly compare Average Hourly Earnings (wage growth) against CPI (inflation). Is their real purchasing power growing or shrinking? How is the current unemployment rate, combined with mortgage rates (implied by 10Y/30Y yields), impacting housing supply (HOSINV) and general consumer sentiment?
    4. NO JARGON EXPLANATIONS: Do not define terms. Assume the reader is institutional.
    5. BE PRECISE & EXHAUSTIVE: Ensure all 9 sections below are covered with dense, insightful logic.

    Structure your response exactly as follows:
    1. MACROECONOMIC & LIQUIDITY TRENDS
    2. YIELD OUTLOOK (Short/Medium/Long)
    3. EQUITIES (Must include Prefer/Avoid sectors)
    4. BONDS (Must include Prefer/Avoid tenors)
    5. GOLD & PRECIOUS METALS (Must include Prefer/Avoid)
    6. COMMODITIES (Must include Prefer/Avoid)
    7. CASH & FX (Must include Prefer/Avoid pairs)
    8. PORTFOLIO MIX, SCENARIOS & ACTIONABLE STRATEGY
    9. THE HUMAN ANGLE (Wages, Real Earnings, & Housing)
    """

    print(f"🔄 Requesting analysis from deepseek-v4-pro (Streaming) for {date_str}...")

    try:
        # 6. DeepSeek-v4-pro execution with stream=True
        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-v4-pro",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,  # Elevated for creative/dynamic market narratives
            top_p=0.95,
            max_tokens=16384,
            extra_body={"chat_template_kwargs": {"thinking": False}},
            stream=True
        )
        
        # 7. Handle the stream and aggregate silently (keeps Actions logs clean)
        analysis_content = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                analysis_content += chunk.choices[0].delta.content

        print("✅ Analysis generated successfully. Saving report...")

        # 8. Format and save output
        report = f"============================================================\n"
        report += f"📅 YIELD CURVE DAILY REPORT (DEEPSEEK PRO) - {date_str}\n"
        report += f"============================================================\n\n"
        report += f"📋 AI ANALYSIS:\n{analysis_content}\n"
        report += f"============================================================\n"
        report += f"✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | NVIDIA DeepSeek-V4-Pro\n"

        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_file = f"{report_dir}/deepseek_report_{date_str}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📄 DeepSeek report saved to: {report_file}")

    except Exception as e:
        print(f"\n⚠️ NVIDIA DeepSeek API error: {e}")

if __name__ == "__main__":
    main()
