
import os
import asyncio
from datetime import datetime
from database import SessionLocal
from models_db import WatchAlert, User
from core.market_data_api import get_current_price
from services.telegram_bot import bot
from core.entitlements import get_user_entitlements

# -----------------------------------------------------------------------------
# Watchlist / Entitlement-based Alert Checker
# -----------------------------------------------------------------------------

async def check_watch_alerts():
    """
    Periodic job to check Watchlist Alerts.
    Checks: PENDING alerts -> trigger vs price.
    Action: Send Telegram & Update DB.
    
    [SECURED] filtering by Entitlements (no alerts if plan expired or token not allowed).
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

        # Optimization: Fetch prices once per token
        tokens_to_fetch = set(a.token for a in active)
        prices = {}
        
        async def fetch_price_safe(t):
            try:
                # Assuming get_current_price is blocking I/O
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
            # 2a. Entitlement Check
            # We must load the user to verify if they still have access to this token/timeframe
            # Optimization: could cache user entitlements, but for safety lets check.
            user = db.query(User).filter(User.id == alert.user_id).first()
            if not user:
                continue
                
            # Verify Entitlements
            entitlements = get_user_entitlements(user)
            offerings = entitlements.get("offerings", [])
            
            # Check if ANY offering covers this token + timeframe?
            # WatchAlert has 'token' and 'timeframe'.
            # We need to see if user has an ACTIVE offering that includes this token.
            
            # Helper: Is (token, timeframe) in offerings?
            is_allowed = False
            for off in offerings:
                # off['tokens'] is list of strings, off['timeframe'] is string
                if (alert.timeframe == off["timeframe"]) and (alert.token in off["tokens"]):
                    is_allowed = True
                    break
            
            if not is_allowed:
                # Silent skip, or expire? 
                # If plan downgraded, maybe we shouldn't alert.
                # print(f"[ALERTS] Skip {alert.id}: User {alert.user_id} lost entitlement for {alert.token} {alert.timeframe}")
                continue

            # 2b. Price Check
            current_price = prices.get(alert.token)
            if not current_price:
                continue
                
            is_triggered = False
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
                
                chat_id = user.telegram_chat_id 
                # Fallback for dev/testing
                if not chat_id:
                     chat_id = os.getenv("TELEGRAM_DEFAULT_CHAT_ID")

                if chat_id:
                    msg = (
                        f"🚨 <b>WATCH ALERT</b>\n\n"
                        f"🪙 <b>{alert.token} {alert.side}</b>\n"
                        f"TF: {alert.timeframe}\n"
                        f"Hit: <b>${alert.trigger_price}</b>\n"
                        f"Current: ${current_price}\n"
                        f"<i>Verified Entitlement ✅</i>"
                    )
                    
                    try:
                        await bot.send_message(chat_id, msg)
                        alert.status = "TRIGGERED"
                        alert.fired_at = datetime.utcnow()
                        triggered_count += 1
                    except Exception as e:
                        print(f"[ALERTS] Failed to send Telegram to {chat_id}: {e}")
                else:
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
