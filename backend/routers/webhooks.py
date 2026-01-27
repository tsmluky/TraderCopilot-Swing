from __future__ import annotations

import os
import logging
from datetime import datetime
from typing import Optional

import stripe
from fastapi import APIRouter, Request, Header, HTTPException
from database import SessionLocal
from models_db import User

router = APIRouter()
LOG = logging.getLogger("tradercopilot")


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise HTTPException(
            status_code=500,
            detail={"code": "CONFIG_MISSING", "message": f"Missing env var: {name}"},
        )
    return v


def _infer_plan_from_price_id(price_id: Optional[str]) -> Optional[str]:
    if not price_id:
        return None
    if price_id == os.getenv("STRIPE_PRICE_TRADER"):
        return "TRADER"
    if price_id == os.getenv("STRIPE_PRICE_PRO"):
        return "PRO"
    return None


def _apply_subscription_state(
    user: User,
    *,
    subscription_status: str,
    price_id: Optional[str],
    current_period_end: Optional[int],
    subscription_id: Optional[str],
    customer_id: Optional[str],
) -> None:
    now = datetime.utcnow()

    if customer_id:
        user.stripe_customer_id = customer_id
        user.billing_provider = "stripe"
    if subscription_id:
        user.stripe_subscription_id = subscription_id
    if price_id:
        user.stripe_price_id = price_id

    active_like = subscription_status in ("active", "trialing")
    plan_from_price = _infer_plan_from_price_id(price_id) if active_like else None

    if active_like and plan_from_price:
        user.plan = plan_from_price
        user.plan_status = "active"
        if current_period_end:
            user.plan_expires_at = datetime.utcfromtimestamp(int(current_period_end))
        else:
            user.plan_expires_at = user.plan_expires_at or now
    else:
        user.plan = "FREE"
        user.plan_status = "inactive"
        user.plan_expires_at = now


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
):
    stripe.api_key = _require_env("STRIPE_SECRET_KEY")
    webhook_secret = _require_env("STRIPE_WEBHOOK_SECRET")

    payload = await request.body()
    if not stripe_signature:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NO_SIGNATURE",
                "message": "Missing Stripe-Signature header"
            }
        )

    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, webhook_secret)
    except Exception as e:
        LOG.warning("Stripe webhook signature verification failed: %s", str(e))
        raise HTTPException(status_code=400, detail={"code": "BAD_SIGNATURE", "message": "Invalid signature"})

    ev_type = event.get("type")
    obj = (event.get("data") or {}).get("object") or {}

    db = SessionLocal()
    try:
        # 1) Checkout completed: Link user <-> customer
        if ev_type == "checkout.session.completed":
            user_id = None
            meta = obj.get("metadata") or {}
            if meta.get("user_id"):
                try:
                    user_id = int(meta.get("user_id"))
                except Exception:
                    user_id = None
            if not user_id and obj.get("client_reference_id"):
                try:
                    user_id = int(obj.get("client_reference_id"))
                except Exception:
                    user_id = None

            if not user_id:
                LOG.warning("checkout.session.completed without user_id; ignoring")
                return {"received": True}

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                LOG.warning("User not found for webhook user_id=%s", user_id)
                return {"received": True}

            sub_id = obj.get("subscription")
            cust_id = obj.get("customer")

            price_id = None
            status = "unknown"
            current_period_end = None

            if sub_id:
                sub = stripe.Subscription.retrieve(sub_id, expand=["items.data.price"])
                status = str(sub.get("status") or "")
                current_period_end = sub.get("current_period_end")

                items = (sub.get("items") or {}).get("data") or []
                if items:
                    price_id = (items[0].get("price") or {}).get("id")

            _apply_subscription_state(
                user,
                subscription_status=status,
                price_id=price_id,
                current_period_end=current_period_end,
                subscription_id=sub_id,
                customer_id=cust_id,
            )
            db.commit()
            return {"received": True}

        # 2) Subscription Updates (Renewals, Cancellations, Downgrades)
        elif ev_type in ["customer.subscription.updated", "customer.subscription.deleted"]:
            cust_id = obj.get("customer")
            if not cust_id:
                return {"received": True}
            
            # Find user by Stripe Customer ID
            user = db.query(User).filter(User.stripe_customer_id == cust_id).first()
            if not user:
                LOG.warning(f"Webhook {ev_type}: No user found for customer {cust_id}")
                return {"received": True}
            
            # Extract status directly from event object (it IS the subscription)
            status = obj.get("status")
            current_period_end = obj.get("current_period_end")
            items = (obj.get("items") or {}).get("data") or []
            price_id = (items[0].get("price") or {}).get("id") if items else None
            
            _apply_subscription_state(
                user,
                subscription_status=status,
                price_id=price_id,
                current_period_end=current_period_end,
                subscription_id=obj.get("id"),
                customer_id=cust_id
            )
            db.commit()
            LOG.info(f"Updated subscription for user {user.id} to status: {status}")
            return {"received": True}

        return {"received": True}
    except Exception as e:
        LOG.error(f"Webhook Handler Failed: {e}")
        return {"received": True}
    finally:
        db.close()