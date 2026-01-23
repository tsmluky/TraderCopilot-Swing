TraderCopilot Backend v0.7 (MVP 80/20) — 2025-11-18T22:39:19Z

ENDPOINTS (contratos):
  POST /analyze/lite
  POST /analyze/pro
  POST /analyze/advisor
  GET  /logs/{mode}/{token}   (mode ∈ LITE|PRO|ADVISOR|EVALUATED; token ∈ eth|btc|sol|xau)
  POST /notify/telegram

Cómo iniciar:
  pwsh backend/tools/start_dev.ps1 -Port 8010

Env vars: ver backend/.env.example
