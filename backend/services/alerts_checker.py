
import os
import asyncio
from datetime import datetime
from database import SessionLocal
from models_db import WatchAlert, User
from core.market_data_api import get_current_price
from services.telegram_bot import bot

async def check_watch_alerts():
    """
    Periodic job to check Watchlist Alerts.
    Checks: PENDING alerts -> trigger vs price.
    Action: Send Telegram & Update DB.
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # 1. Expire old alerts
        expired = db.query(WatchAlert).filter(
            WatchAlert.status == "PENDING",
            WatchAlert.expires_at < now
        ).all()
        for exp in expired:
            exp.status = "EXPIRED"
        
        if expired:
            db.commit()
            print(f"[ALERTS] Expired {len(expired)} alerts.")

        # 2. Check Active Alerts
        active = db.query(WatchAlert).filter(WatchAlert.status == "PENDING").all()
        if not active:
            return

        # Optimization: Group by Token to fetch price once
        tokens_to_fetch = set(a.token for a in active)
        prices = {}
        
        # [FIX] Run blocking network calls in ThreadPool to avoid freezing FastAPI
        # Fetch prices in parallel for speed
        async def fetch_price_safe(t):
            try:
                # Use asyncio.to_thread for blocking Sync IO
                return t, await asyncio.to_thread(get_current_price, t)
            except Exception as e:
                print(f"[ALERTS] Error fetching price for {t}: {e}")
                return t, None

        tasks = [fetch_price_safe(t) for t in tokens_to_fetch]
        results = await asyncio.gather(*tasks)
        
        for token, price in results:
            if price and price > 0:
                prices[token] = price

        triggered_count = 0
        
        for alert in active:
            current_price = prices.get(alert.token)
            if not current_price:
                continue
                
            is_triggered = False
            
            # TRIGGER LOGIC
            # Long: Price >= Trigger
            # Short: Price <= Trigger
            if alert.side.upper() == "LONG":
                if current_price >= alert.trigger_price:
                    is_triggered = True
            elif alert.side.upper() == "SHORT":
                if current_price <= alert.trigger_price:
                    is_triggered = True
            
            if is_triggered:
                print(
                    f"[ALERTS] TRIGGERED! {alert.token} {alert.side} @ {current_price} "
                    f"(Target: {alert.trigger_price})"
                )
                
                # Retrieve User for Chat ID
                user = db.query(User).filter(User.id == alert.user_id).first()
                chat_id = user.telegram_chat_id if user else None
                
                # Fallback to default channel if no user chat_id (or for testing)
                # But typically WatchAlerts are personal. If no chat_id, we can't notify personally.
                # using env var fallback:
                if not chat_id:
                     chat_id = os.getenv("TELEGRAM_DEFAULT_CHAT_ID")

                if chat_id:
                    msg = (
                        f"🚨 <b>WATCH ALERT TRIGGERED</b>\n\n"
                        f"🪙 <b>{alert.token} {alert.side}</b>\n"
                        f"🎯 Trigger Reached: <b>${alert.trigger_price}</b>\n"
                        f"📊 Current: ${current_price}\n"
                        f"Strategy: {alert.strategy_id}\n\n"
                        f"<i>Check your dashboard for confirmation.</i>"
                    )
                    
                    try:
                        await bot.send_message(chat_id, msg)
                        alert.status = "TRIGGERED"
                        alert.fired_at = datetime.utcnow()
                        triggered_count += 1
                    except Exception as e:
                        print(f"[ALERTS] Failed to send Telegram to {chat_id}: {e}")
                else:
                    # Mark triggered anyway so we don't loop forever, or keep pending?
                    # Let's mark triggered to indicate the event happened.
                    alert.status = "TRIGGERED" 
                    alert.fired_at = datetime.utcnow()
                    triggered_count += 1
            
            alert.last_check_at = datetime.utcnow()
            
        if triggered_count > 0:
            db.commit()
            print(f"[ALERTS] Fired {triggered_count} alerts.")
            
    except Exception as e:
        print(f"[ALERTS] Job Error: {e}")
    finally:
        db.close()
