#!/bin/bash

# Telegram Bot Webhook Setup Script
# Run this ONCE after deploying to Railway to configure the webhook

TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
RAILWAY_DOMAIN="your-app.up.railway.app"

# Set webhook URL
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://${RAILWAY_DOMAIN}/telegram/webhook\"}"

echo ""
echo "✅ Webhook configured!"
echo "Test it by sending /myid to your bot in Telegram"
