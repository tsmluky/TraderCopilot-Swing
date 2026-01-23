import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar .env desde el directorio padre
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY no encontrada en .env")
    exit(1)

print(f"🔑 Key encontrada: {api_key[:5]}...{api_key[-3:]}")

try:
    genai.configure(api_key=api_key)
    print("📡 Conectando a Google AI Studio...")

    models = list(genai.list_models())

    print("\n✅ Modelos Disponibles:")
    for m in models:
        print(f" - {m.name}")


except Exception as e:
    print(f"\n❌ Error listando modelos: {e}")
