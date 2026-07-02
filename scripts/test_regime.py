from fetch_yields import load_history
from analyze_regime import compute_spreads, classify_regime, get_asset_recommendations

# Load history
df = load_history()
if not df.empty:
    df = compute_spreads(df)
    latest = df.iloc[-1]
    regime, confidence, explanation = classify_regime(latest, df)
    
    print(f"\n📅 Date: {latest['date']}")
    print(f"10Y: {latest['10Y']:.2f}% | 3M: {latest['3M']:.2f}% | Spread: {latest['10Y_3M_spread']:.2f}%")
    print(f"\n🔍 Regime: {regime} (Confidence: {confidence:.2f})")
    print(f"Explanation: {explanation}")
    
    print("\n📊 Asset Recommendations:")
    recs = get_asset_recommendations(regime)
    for asset, action in recs.items():
        print(f"  {asset.capitalize()}: {action}")
else:
    print("No historical data found. Run fetch_yields.py first.")
