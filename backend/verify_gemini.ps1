
# verify_gemini.ps1
# Smoke test for Gemini Integration

$env:PYTHONPATH = "$PWD;$PWD\backend"

Write-Host "--- TEST: GEMINI ADVISOR ---" -ForegroundColor Cyan
python -c "import sys; sys.path.append('.'); from dotenv import load_dotenv; load_dotenv('backend/.env'); from backend.core.llm_client_gemini import call_llm; print(call_llm('advisor', [{'role': 'user', 'content': 'Hello'}]))"

Write-Host "`n--- TEST: GEMINI PRO ---" -ForegroundColor Cyan
python -c "import sys; sys.path.append('.'); from dotenv import load_dotenv; load_dotenv('backend/.env'); from backend.core.llm_client_gemini import call_llm; print(call_llm('pro', [{'role': 'user', 'content': 'Brief analysis'}]))"

Write-Host "`nDone."
