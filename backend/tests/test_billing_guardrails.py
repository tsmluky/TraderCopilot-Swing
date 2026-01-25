import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

def _set_env_missing_stripe(monkeypatch):
    # limpiamos env vars típicas para forzar guardrail de config
    keys = [
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "STRIPE_PRICE_ID",
        "STRIPE_SUCCESS_URL",
        "STRIPE_CANCEL_URL",
        "STRIPE_API_KEY",
        "STRIPE_PRICE_ID_TRADER",
        "STRIPE_PRICE_ID_PRO",
    ]
    for k in keys:
        monkeypatch.delenv(k, raising=False)


def _import_billing_module():
    for modname in ("backend.routers.billing", "routers.billing"):
        try:
            return importlib.import_module(modname)
        except Exception:
            continue
    return None


def test_billing_module_exists():
    mod = _import_billing_module()
    assert mod is not None, "No se pudo importar billing router (backend.routers.billing o routers.billing)."


def test_guardrail_require_env(monkeypatch):
    mod = _import_billing_module()
    if mod is None:
        pytest.skip("Billing module no importable.")

    _set_env_missing_stripe(monkeypatch)

    fn = getattr(mod, "_require_env", None) or getattr(mod, "require_env", None)
    if fn is None:
        pytest.skip("No existe _require_env/require_env en billing.py")

    with pytest.raises(HTTPException) as e:
        fn("STRIPE_SECRET_KEY")

    assert e.value.status_code in (500, 400)

    detail = e.value.detail
    if isinstance(detail, dict):
        code = detail.get("code")
    elif isinstance(detail, str):
        code = detail.split(":")[0].strip()
    else:
        code = None

    assert code in (None, "CONFIG_MISSING", "STRIPE_CONFIG_MISSING"), f"Código inesperado en guardrail: {code}"


def test_guardrail_validate_user_schema():
    mod = _import_billing_module()
    if mod is None:
        pytest.skip("Billing module no importable.")

    fn = getattr(mod, "_validate_user_schema", None) or getattr(mod, "validate_user_schema", None)
    if fn is None:
        pytest.skip("No existe _validate_user_schema/validate_user_schema en billing.py")

    user = SimpleNamespace(id=1, email="x@y.com")
    with pytest.raises(HTTPException) as e:
        fn(user)

    assert e.value.status_code in (500, 400)

    detail = e.value.detail
    if isinstance(detail, dict):
        code = detail.get("code")
    elif isinstance(detail, str):
        code = detail.split(":")[0].strip()
    else:
        code = None

    assert code in (None, "BILLING_SCHEMA_OUTDATED"), f"Código inesperado schema guardrail: {code}"
