import os, sys
from openai import OpenAI

def transmit_payload_to_ai():
    # Accept command line arguments
    if len(sys.argv) >= 3:
        prompt_file_path = sys.argv[1]
        date_str = sys.argv[2]
    else:
        print("❌ Missing arguments")
        sys.exit(1)
    
    ai_report_path = f"reports/ai_market_analysis_{date_str}.txt"
    
    # Check if report already exists
    if os.path.exists(ai_report_path):
        print(f"✅ AI report already exists for {date_str}")
        return
    
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt = f.read()
    
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    if not NVIDIA_API_KEY:
        print("⚠️ NVIDIA_API_KEY not set")
        return

    client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)

    print(f"🔄 Generating AI analysis for {date_str}...")
    
    try:
        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-v4-pro",
            messages=[{"role": "system", "content": "You are an elite institutional market strategist specialized in the Indian National Stock Exchange (NSE) derivatives data analysis."},
                     {"role": "user", "content": prompt}],
            temperature=0.8, top_p=0.95, max_tokens=30000,
            extra_body={"chat_template_kwargs": {"thinking": True}}, stream=True
        )

        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        
        with open(ai_report_path, "w", encoding="utf-8") as f:
            f.write(full_response)
        print(f"✅ AI analysis saved to: {ai_report_path}")
        
    except Exception as err:
        print(f"❌ Error: {err}")

if __name__ == "__main__":
    transmit_payload_to_ai()
