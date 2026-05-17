import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro", "gemini-flash-latest", "gemini-2.0-flash", "gemini-pro-latest"]
    
    for model_name in models:
        print(f"Testing {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("test", generation_config={"max_output_tokens": 10})
            print(f"  SUCCESS: {model_name} is working!")
            break
        except Exception as e:
            print(f"  FAILED: {model_name} -> {e}")
