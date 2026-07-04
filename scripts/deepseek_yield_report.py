import os
from datetime import datetime
import pandas as pd
from openai import OpenAI

def main():
    print("🚀 Starting parallel DeepSeek yield report...")
    
    # 1. Setup API Client
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    if not NVIDIA_API_KEY:
        print("⚠️ No NVIDIA_API_KEY found. Check GitHub Secrets.")
        return

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=NVIDIA_API_KEY
    )

    # 2. Load the freshly updated CSV data
    csv_file = "data/yield_history.csv"
    if not os.path.exists(csv_file):
        print(f"⚠️ {csv_file} not found. Ensure fetch_all_data ran successfully.")
        return

    df = pd.read_csv(csv_file)
    if df.empty:
        print("⚠️ Dataframe is empty.")
        return

    # 3. Helpers for safely extracting historical data
    def safe_val(data, col, rows_back):
        if col in data.columns and len(data) > rows_back:
            val = data[col].iloc[-(rows_back + 1)]
            return f"{val:.2f}" if pd.notnull(val) else "N/A"
        return "N/A"

    def fmt(val):
        return f"{val:.3f}" if pd.notnull(val) else "N/A"

    # 4. Extract data for the prompt
    latest = df.iloc[-1]
    date_str = latest['date']
    last_30 = df.tail(30).to_string(index=False)

    s30_2 = latest.get('30Y', 0) - latest.get('2Y', 0)
    s10_2 = latest.get('10Y', 0) - latest.get('2Y', 0)
    s10_3 = latest.get('10Y', 0) - latest.get('3M', 0)
    s30_5 = latest.get('30Y', 0) - latest.get('5Y', 0)

    dxy_str = f"{latest.get('DXY'):.2f}" if pd.notnull(latest.get('DXY')) else "N/A"
    fed_str = f"{latest.get('FEDFUNDS'):.2f}" if pd.notnull(latest.get('FEDFUNDS')) else "N/A"

    macro_snapshot = f"""
    --- CURRENT DATA vs 1 MONTH AGO vs 1 YEAR AGO ---
    10Y Yield: {latest.get('10Y', 0):.2f}% (1M Ago: {safe_val(df, '10Y', 21)}%, 1Y Ago: {safe_val(df, '10Y', 252)}%)
    2Y Yield: {latest.get('2Y', 0):.2f}% (1M Ago: {safe_val(df, '2Y', 21)}%, 1Y Ago: {safe_val(df, '2Y', 252)}%)
    DXY (USD): {dxy_str} (1M Ago: {safe_val(df, 'DXY', 21)}, 1Y Ago: {safe_val(df, 'DXY', 252)})
    
    M2 Money Supply (Trillions): {fmt(latest.get('M2SL'))} (1M Ago: {safe_val(df, 'M2SL', 21)}, 1Y Ago: {safe_val(df, 'M2SL', 252)})
    Fed Balance Sheet - WALCL (Trillions): {fmt(latest.get('WALCL'))} (1M Ago: {safe_val(df, 'WALCL', 21)})
    Unemployment Rate: {fmt(latest.get('UNRATE'))}% (1M Ago: {safe_val(df, 'UNRATE', 21)}%, 1Y Ago: {safe_val(df, 'UNRATE', 252)}%)
    CPI (AUCSL): {fmt(latest.get('CPIAUCSL'))} (1Y Ago: {safe_val(df, 'CPIAUCSL', 252)})
    Nonfarm Payrolls (Millions): {fmt(latest.get('PAYEMS'))}
    """

    prompt = f"""
    You are a top-tier macro strategist. Analyze the US Treasury yield curve and macroeconomic data.

    Last 30 days of raw yield data:
    {last_30}

    Current Snapshot: 
    3M={latest.get('3M', 0):.2f}%, 2Y={latest.get('2Y', 0):.2f}%, 5Y={latest.get('5Y', 0):.2f}%, 10Y={latest.get('10Y', 0):.2f}%, 30Y={latest.get('30Y', 0):.2f}%
    Spreads: 30Y-2Y={s30_2:.2f}%, 10Y-2Y={s10_2:.2f}%, 10Y-3M={s10_3:.2f}%, 30Y-5Y={s30_5:.2f}%
    Fed Funds Rate: {fed_str}%

    Pre-calculated Historical Trends:
    {macro_snapshot}

    Provide a complete, vivid, and highly authentic 360° analysis backed by the data provided.

    For your analysis, you MUST follow these formatting constraints to ensure completion:
    1. Do NOT write long introduction or transition paragraphs. Go straight to the data points.
    2. Use concise, punchy, high-impact bullet points for all sub-sections.
    3. Explicitly weave in the pre-calculated MoM and YoY percentage/basis point changes inside those bullets.
    4. Keep descriptions dense with macro logic but physically short so all 9 sections fit perfectly.

    Structure your response exactly as follows:
    1. MACROECONOMIC & LIQUIDITY TRENDS
    2. YIELD OUTLOOK (Short/Medium/Long)
    3. EQUITIES
    4. BONDS
    5. GOLD & PRECIOUS METALS
    6. COMMODITIES
    7. CASH & FX
    8. PORTFOLIO MIX & ACTIONABLE STRATEGY
    9. SCENARIO ANALYSIS
    """

    print(f"🔄 Requesting analysis from NVIDIA DeepSeek for {date_str}...")

    try:
        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.95,
            max_tokens=8192,
            extra_body={"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}},
            stream=False
        )
        
        message = completion.choices[0].message
        reasoning = getattr(message, "reasoning", None) or getattr(message, "reasoning_content", None)
        analysis_content = message.content

        # 5. Format the final output
        report = f"============================================================\n"
        report += f"📅 YIELD CURVE DAILY REPORT (DEEPSEEK) - {date_str}\n"
        report += f"============================================================\n\n"
        
        if reasoning:
            report += f"🧠 DEEPSEEK REASONING (CHAIN OF THOUGHT):\n{reasoning}\n\n"
            report += f"============================================================\n\n"
            
        report += f"📋 AI ANALYSIS:\n{analysis_content}\n"
        report += f"============================================================\n"
        report += f"✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | NVIDIA DeepSeek\n"

        # 6. Save to a distinct file
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_file = f"{report_dir}/deepseek_report_{date_str}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📄 DeepSeek report saved to: {report_file}")

    except Exception as e:
        print(f"⚠️ NVIDIA DeepSeek API error: {e}")

if __name__ == "__main__":
    main()
