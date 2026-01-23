# Telegram Bot Webhook Configuration

## Overview
The Telegram bot is now integrated directly into your FastAPI backend using **webhooks** instead of polling. This means:
- ✅ No separate process needed
- ✅ No additional Railway deployment
- ✅ Telegram calls your API when users send commands
- ✅ More efficient and scalable

## Setup Instructions

### 1. Get Your Bot Token
If you don't have one:
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Add Token to Railway
1. Go to your Railway project
2. Navigate to **Variables** tab
3. Add: `TELEGRAM_BOT_TOKEN` = `your_token_here`
4. Deploy changes

### 3. Configure Webhook (ONE-TIME SETUP)
After your Railway deployment is live, run this command **once** from your terminal:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-railway-domain.up.railway.app/telegram/webhook"}'
```

Replace:
- `<YOUR_BOT_TOKEN>` with your actual bot token
- `your-railway-domain.up.railway.app` with your Railway domain

### 4. Test It
1. Open Telegram
2. Find your bot and send `/myid`
3. The bot should respond with your Chat ID
4. Copy the Chat ID and paste it in **TraderCopilot Settings > Telegram Integration**

## Available Commands
- `/start` - Show welcome message
- `/myid` - Get your Chat ID for notifications

## Troubleshooting

**Bot doesn't respond:**
- Verify `TELEGRAM_BOT_TOKEN` is set in Railway
- Check webhook is configured: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- View Railway logs for `[TELEGRAM WEBHOOK]` messages

**Permission errors:**
- Make sure the Railway URL uses HTTPS (required by Telegram)
- Verify the webhook endpoint is publicly accessible

## Local Development
For local testing with ngrok:
```bash
# Start ngrok
ngrok http 8000

# Set webhook to ngrok URL
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d '{"url": "https://your-ngrok-url.ngrok.io/telegram/webhook"}'
```

## Removing Webhook
To switch back to polling or disable the bot:
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```
