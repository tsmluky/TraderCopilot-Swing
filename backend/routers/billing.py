from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, Dict

import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models_db import User
from routers.auth_new import get_current_user

router = APIRouter()


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise HTTPException(
            status_code=500,
            detail={"code": "CONFIG_MISSING", "message": f"Missing env var: {name}"},
        )
    return v


def _validate_user_schema(user: User):
    """
    Guardrail: Ensure runtime User object actually has Stripe fields.
    If database schema is outdated, accessing these might fail or be None 
    (though SQLAlchemy mapped attributes usually exist as None if not in __dict__).
    This is mostly to catch if the ORM definition itself was out of sync, 
    but we just updated models_db.py. 
    The real runtime error happens if we try to access a column that doesn't exist in the DB 
    and SQLAlchemy queries it.
    """
    try:
        # Just accessing them to trigger potential lazy load errors or AttributeError
        _ = user.stripe_customer_id
        _ = user.billing_provider
    except Exception as e:
        print(f"[BILLING CRITICAL] Schema mismatch: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "BILLING_SCHEMA_OUTDATED", 
                "message": "User schema missing Stripe fields. Run migrations."
            }
        )


def _stripe_init() -> None:
    stripe.api_key = _require_env("STRIPE_SECRET_KEY")


def _plan_to_price_id(plan_upper: str) -> str:
    plan_upper = (plan_upper or "").upper()
    if plan_upper == "TRADER":
        return _require_env("STRIPE_PRICE_TRADER")
    if plan_upper == "PRO":
        return _require_env("STRIPE_PRICE_PRO")
    raise HTTPException(
        status_code=400,
        detail={"code": "INVALID_PLAN", "message": "Plan must be TRADER or PRO."},
    )


def _infer_plan_from_price_id(price_id: Optional[str]) -> Optional[str]:
    if not price_id:
        return None
    if price_id == os.getenv("STRIPE_PRICE_TRADER"):
        return "TRADER"
    if price_id == os.getenv("STRIPE_PRICE_PRO"):
        return "PRO"
    return None


def _apply_subscription_state(
    db: Session,
    user: User,
    *,
    subscription_status: str,
    price_id: Optional[str],
    current_period_end: Optional[int],
    subscription_id: Optional[str],
    customer_id: Optional[str],
) -> Dict[str, str]:
    """
    MVP strict:
    - active/trialing => TRADER/PRO (por price_id)
    - resto => FREE + inactive
    """
    now = datetime.utcnow()

    if customer_id:
        user.stripe_customer_id = customer_id
    if subscription_id:
        user.stripe_subscription_id = subscription_id
    if price_id:
        user.stripe_price_id = price_id

    active_like = subscription_status in ("active", "trialing")
    plan_from_price = _infer_plan_from_price_id(price_id) if active_like else None

    if active_like and plan_from_price:
        user.plan = plan_from_price
        user.plan_status = "active"
        user.billing_provider = "stripe"
        if current_period_end:
            user.plan_expires_at = datetime.utcfromtimestamp(int(current_period_end))
        else:
            user.plan_expires_at = user.plan_expires_at or now
    else:
        user.plan = "FREE"
        user.plan_status = "inactive"
        user.plan_expires_at = now

    db.commit()
    db.refresh(user)

    return {"plan": user.plan, "plan_status": user.plan_status or ""}


class CheckoutRequest(BaseModel):
    plan: str = Field(..., description="TRADER or PRO")
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class UrlResponse(BaseModel):
    url: str


@router.post("/checkout-session", response_model=UrlResponse)
def create_checkout_session(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _stripe_init()

    plan_upper = (payload.plan or "").upper()
    price_id = _plan_to_price_id(plan_upper)

    success_url = payload.success_url or _require_env("STRIPE_SUCCESS_URL")
    cancel_url = payload.cancel_url or _require_env("STRIPE_CANCEL_URL")

    # Ensure customer exists
    if current_user.stripe_customer_id:
        customer_id = current_user.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name or None,
            metadata={"user_id": str(current_user.id)},
        )
        customer_id = customer["id"]
        current_user.stripe_customer_id = customer_id
        current_user.billing_provider = "stripe"
        db.commit()

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        allow_promotion_codes=True,
        client_reference_id=str(current_user.id),
        metadata={"user_id": str(current_user.id), "plan": plan_upper},
    )

    return {"url": session["url"]}


@router.post("/portal-session", response_model=UrlResponse)
def create_portal_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _stripe_init()

    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_BILLING_CUSTOMER", "message": "No Stripe customer attached."},
        )

    return_url = _require_env("STRIPE_PORTAL_RETURN_URL")

    sess = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=return_url,
    )
    return {"url": sess["url"]}


@router.post("/sync")
def sync_billing_state(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Útil justo después de volver del Checkout:
    evita que el frontend te mande a /trial-expired por una carrera webhook.
    """
    _stripe_init()

    if not current_user.stripe_customer_id:
        return {"status": "noop", "reason": "no_customer"}

    subs = stripe.Subscription.list(customer=current_user.stripe_customer_id, status="all", limit=10)
    data = subs.get("data") or []

    picked = None
    foreach = data
    for s in foreach:
        if s.get("status") in ("active", "trialing"):
            picked = s
            break
    if not picked and data:
        picked = data[0]

    if not picked:
        _apply_subscription_state(
            db,
            current_user,
            subscription_status="canceled",
            price_id=None,
            current_period_end=None,
            subscription_id=None,
            customer_id=current_user.stripe_customer_id,
        )
        return {"status": "synced", "plan": current_user.plan, "plan_status": current_user.plan_status}

    price_id = None
    try:
        items = (picked.get("items") or {}).get("data") or []
        if items:
            price_id = items[0].get("price", {}).get("id")
    except Exception:
        price_id = None

    _apply_subscription_state(
        db,
        current_user,
        subscription_status=str(picked.get("status") or ""),
        price_id=price_id,
        current_period_end=picked.get("current_period_end"),
        subscription_id=picked.get("id"),
        customer_id=picked.get("customer"),
    )

    return {"status": "synced", "plan": current_user.plan, "plan_status": current_user.plan_status}