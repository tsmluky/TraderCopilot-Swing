from datetime import timedelta, datetime
from typing import Annotated

import fastapi
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from models_db import User
from pydantic import BaseModel
from database import get_db, SessionLocal
from core.schemas import UserCreate, UserResponse
from core.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)
from core.limiter import limiter

# Entitlements Endpoint
# ... (imports)
from core.entitlements import get_user_entitlements, get_plan_entitlements
from core.trial_policy import get_access_tier


router = APIRouter(prefix="/auth", tags=["Auth"])

# NOTE: tokenUrl is mainly for OpenAPI docs. Keeping relative is OK, but absolute is safer.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def _safe_name(obj) -> str:
    """
    Compat layer: algunos esquemas/modelos en DEV pueden no tener .name.
    Nunca debe romper auth.
    """
    v = getattr(obj, "name", None)
    if v and str(v).strip():
        return str(v).strip()
    em = getattr(obj, "email", "") or ""
    if "@" in em:
        return em.split("@")[0]
    return em or "user"


async def get_current_user(
    token: Annotated[str, fastapi.Depends(oauth2_scheme)],
    db: Session = fastapi.Depends(get_db),
):
    """Verifica el token JWT y retorna el usuario actual."""
    from jose import JWTError, jwt

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            print("[AUTH] Token missing 'sub' claim")
            raise credentials_exception
    except JWTError as e:
        print(f"[AUTH] JWT Decode Error: {e}")
        raise credentials_exception

    result = db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user is None:
        print(f"[AUTH] User {email} not found in DB")
        raise credentials_exception

    return user

@router.post("/token")
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,  # Required for SlowAPI
    form_data: Annotated[OAuth2PasswordRequestForm, fastapi.Depends()],
    db: Session = fastapi.Depends(get_db),
):
    """Endpoint estandar OAuth2 para login (email/password)."""
    result = db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    plan_upper = (getattr(user, "plan", None) or "FREE").upper()
    tier = get_access_tier(user)
    
    # Get entitlements
    entitlements = get_plan_entitlements(tier)
    allowed_tokens = entitlements["tokens"]
    allowed_timeframes = entitlements["timeframes"]

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": _safe_name(user),
            "role": getattr(user, "role", "user"),
            # IMPORTANT: keep uppercase canonical plan; frontend can format for display
            "plan": plan_upper,
            "plan_status": ("expired" if tier == "TRIAL_EXPIRED" else "active"),
            "allowed_tokens": allowed_tokens,
            "allowed_timeframes": allowed_timeframes,
            "created_at": getattr(user, "created_at", None),
        },
    }

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    """
    Minimal whoami endpoint used by frontend to validate session.
    Returns the authenticated user payload.
    """
    tier = get_access_tier(current_user)
    entitlements = get_plan_entitlements(tier)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": _safe_name(current_user),
        "role": getattr(current_user, "role", "user"),
        "plan": getattr(current_user, "plan", "FREE"),
        "plan_status": ("expired" if tier == "TRIAL_EXPIRED" else "active"),
        "allowed_tokens": entitlements["tokens"],
        "allowed_timeframes": entitlements["timeframes"],
        "telegram_chat_id": getattr(current_user, "telegram_chat_id", None),
        "telegram_username": getattr(current_user, "telegram_username", None),
        "timezone": getattr(current_user, "timezone", None),
        "plan_expires_at": getattr(current_user, "plan_expires_at", None),
        "created_at": getattr(current_user, "created_at", None),
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: Request, db: Session = fastapi.Depends(get_db)):
    """
    Registra un nuevo usuario en la plataforma.
    """
    try:
        data = await request.json()
        user_data = UserCreate(**data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    email_norm = user_data.email.strip().lower()

    result = db.execute(select(User).where(User.email == email_norm))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_pwd = get_password_hash(user_data.password)

    # === NORMALIZATION ===
    plan_upper = "FREE"
    plan_expires_at = datetime.utcnow() + timedelta(days=7)

    # Compat: UserCreate puede no tener name
    name_val = getattr(user_data, "name", None)
    if not name_val or not str(name_val).strip():
        # default display name: prefix del email
        name_val = email_norm.split("@")[0]

    new_user = User(
        email=email_norm,
        hashed_password=hashed_pwd,
        name=name_val,
        plan=plan_upper,
        plan_expires_at=plan_expires_at,
        created_at=datetime.utcnow(),
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        user_id_created = new_user.id

        try:
            # TODO: Re-enable when seed_default_strategies is properly imported
            # seed_default_strategies(db, new_user)
            pass
        except Exception as seed_err:
            print(
                f"⚠️ [AUTH WARNING] Strategy seeding failed "
                f"for {new_user.email}: {seed_err}"
            )
            db.rollback()
            new_user = db.query(User).filter(User.id == user_id_created).first()
            if not new_user:
                raise HTTPException(status_code=500, detail="User lost after rollback.")
            pass

        tier = get_access_tier(new_user)
        entitlements = get_plan_entitlements(tier)

        return {
            "id": new_user.id,
            "email": new_user.email,
            "name": _safe_name(new_user),
            "role": getattr(new_user, "role", "user"),
            "plan": plan_upper,
            "allowed_tokens": entitlements["tokens"],
            "allowed_timeframes": entitlements["timeframes"],
            "telegram_chat_id": getattr(new_user, "telegram_chat_id", None),
            "timezone": getattr(new_user, "timezone", None),
            "created_at": getattr(new_user, "created_at", None),
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[AUTH ERROR] Register failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

# ... (seed_default_strategies)

# ... (get_sync_db)


def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/me/entitlements")
def read_my_entitlements(
    current_user: User = fastapi.Depends(get_current_user),
    db: Session = fastapi.Depends(get_sync_db),
):
    """
    Diagnóstico de límites y cuotas.
    """
    ent = get_user_entitlements(current_user)
    
    # [FIX] Inject flat list of allowed timeframes for frontend (useAuth hook)
    tier = get_access_tier(current_user)
    plan_ent = get_plan_entitlements(tier)
    
    ent["allowed_timeframes"] = plan_ent["timeframes"]
    ent["allowed_tokens"] = plan_ent["tokens"] # backup
    
    # Feature flags
    from core.entitlements import can_access_telegram, can_use_advisor
    ent["telegram_access"] = can_access_telegram(current_user)
    ent["advisor_access"] = can_use_advisor(current_user)

    return ent


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = fastapi.Depends(get_current_user)):
    """
    Get current user profile (synced with frontend requirements).
    """
    plan_upper = (getattr(current_user, "plan", None) or "FREE").upper()
    tier = get_access_tier(current_user)
    entitlements = get_plan_entitlements(tier)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": _safe_name(current_user),
        "role": getattr(current_user, "role", "user"),
        "plan": plan_upper,
        "allowed_tokens": entitlements["tokens"],
        "allowed_timeframes": entitlements["timeframes"],
        "telegram_chat_id": getattr(current_user, "telegram_chat_id", None),
        "timezone": getattr(current_user, "timezone", None),
        "created_at": getattr(current_user, "created_at", None) or datetime.utcnow(),
    }


class TelegramUpdate(BaseModel):
    chat_id: str


@router.patch("/users/me/plan")
async def update_my_plan(
    new_plan: str,
    db: Session = fastapi.Depends(get_db),
    current_user: User = fastapi.Depends(get_current_user),
):
    """
    Self-service plan update (for subscription upgrades/downgrades).
    """
    valid_plans = ["FREE", "TRADER", "PRO", "OWNER"]
    plan_upper = new_plan.upper()

    if plan_upper not in valid_plans:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan. Must be one of: {', '.join(valid_plans)}",
        )

    current_user.plan = plan_upper
    db.commit()
    db.refresh(current_user)

    return {"message": f"Plan updated to {plan_upper}", "plan": plan_upper}


@router.patch("/users/me/telegram")
async def update_telegram_id(
    payload: TelegramUpdate,
    current_user: User = fastapi.Depends(get_current_user),
    db: Session = fastapi.Depends(get_db),
):
    """
    Updates the connected Telegram Chat ID for the current user.
    """
    current_user.telegram_chat_id = payload.chat_id
    db.commit()
    return {"status": "ok", "telegram_chat_id": current_user.telegram_chat_id}


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


@router.patch("/users/me/password")
async def update_password(
    payload: PasswordUpdate,
    current_user: User = fastapi.Depends(get_current_user),
    db: Session = fastapi.Depends(get_db),
):
    """
    Secure password change.
    """
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
        )

    current_user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"status": "ok", "message": "Password updated successfully"}


class TimezoneUpdate(BaseModel):
    timezone: str


@router.patch("/users/me/timezone")
async def update_timezone(
    payload: TimezoneUpdate,
    current_user: User = fastapi.Depends(get_current_user),
    db: Session = fastapi.Depends(get_db),
):
    """
    Updates the preferred Timezone for the current user.
    """
    current_user.timezone = payload.timezone
    db.commit()
    return {"status": "ok", "timezone": current_user.timezone}


# === PASSWORD RECOVERY ===

class RecoverRequest(BaseModel):
    email: str

class ResetRequest(BaseModel):
    token: str
    new_password: str


@router.post("/recover")
async def request_password_recovery(
    payload: RecoverRequest,
    db: Session = fastapi.Depends(get_db)
):
    """
    1. Check email exists
    2. Generate Short-Lived Token (15m)
    3. Send Email (Hybrid: Console or SMTP)
    """
    user = db.execute(select(User).where(User.email == payload.email)).scalars().first()
    if not user:
        return {"message": "If this email is registered, a recovery link has been sent."}

    access_token_expires = timedelta(minutes=15)
    recovery_token = create_access_token(
        data={"sub": user.email, "scope": "reset_password"},
        expires_delta=access_token_expires
    )

    from core.email_sender import send_recovery_email
    send_recovery_email(user.email, recovery_token)

    return {"message": "Recovery email sent."}


@router.post("/reset")
async def reset_password(
    payload: ResetRequest,
    db: Session = fastapi.Depends(get_db)
):
    """
    1. Verify Token (Exp + Scope)
    2. Reset Password
    """
    from jose import JWTError, jwt

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
    )

    try:
        data = jwt.decode(payload.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = data.get("sub")
        scope = data.get("scope")

        if email is None or scope != "reset_password":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.execute(select(User).where(User.email == email)).scalars().first()
    if not user:
        raise credentials_exception

    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()

    return {"message": "Password updated successfully."}




























