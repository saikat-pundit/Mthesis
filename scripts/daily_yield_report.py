import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_yields import fetch_all_yields, save_to_csv, load_history, get_most_recent_available_date
from analyze_regime import compute_spreads, classify_regime
from call_deepseek import generate_daily_report

def main():
    print("🚀 Starting daily yield curve report...")
    
    # Get most recent available date
    date = get_most_recent_available_date()
    print(f"📅 Most recent available date: {date}")
    
    # Fetch yields
    yields = fetch_all_yields(date)
    if yields.get('10Y') is None:
        print("❌ Failed to fetch 10Y yield data. Check FRED API key.")
        return
    
    # Save to CSV
    df = save_to_csv(yields)
    
    # Load history and compute spreads
    df = load_history()
    df = compute_spreads(df)
    
    # Get latest data
    latest = df.iloc[-1]
    regime, confidence, explanation = classify_regime(latest, df)
    
    # Generate report
    report = generate_daily_report(
        yields=yields,
        regime=regime,
        confidence=confidence,
        explanation=explanation,
        history_df=df
    )
    
    # Print report
    print(report)
    
    # Save report to file
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_file = f"{report_dir}/report_{date}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"📄 Report saved to: {report_file}")
    
    # Also save latest summary to a JSON
    summary = {
        "date": date,
        "yields": yields,
        "spreads": {
            "10Y_3M": yields['10Y_3M_spread'] if '10Y_3M_spread' in yields else None,
            "10Y_2Y": yields['10Y_2Y_spread'] if '10Y_2Y_spread' in yields else None
        },
        "regime": regime,
        "confidence": confidence,
        "explanation": explanation
    }
    import json
    with open(f"{report_dir}/summary_{date}.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Done!")

if __name__ == "__main__":
    main()
