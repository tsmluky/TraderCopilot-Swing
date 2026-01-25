import re
from pathlib import Path



def _find_stripe_migration_files():
    candidates = [
        Path("backend/alembic/versions"),
        Path("alembic/versions"),
    ]
    out = []
    for base in candidates:
        if base.exists():
            out += list(base.glob("*.py"))

    stripe_files = []
    for f in out:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "stripe_customer_id" in txt or "stripe_subscription_id" in txt or "manual_stripe" in txt:
            stripe_files.append((f, txt))
    return stripe_files


def _parse_assignment(text: str, name: str):
    m = re.search(rf"^{name}\s*=\s*(['\"])(.*?)\1\s*$", text, re.MULTILINE)
    if not m:
        return None
    return m.group(2)


def test_alembic_stripe_migration_exists_and_has_down_revision():
    files = _find_stripe_migration_files()
    assert files, (
        "No se encontró ninguna migración Alembic con campos Stripe "
        "(stripe_customer_id/stripe_subscription_id)."
    )

    ok_any = False
    problems = []

    for (f, txt) in files:
        rev = _parse_assignment(txt, "revision")
        down = _parse_assignment(txt, "down_revision")

        if rev is None:
            problems.append(f"{f}: no se pudo parsear revision")
            continue

        if down in (None, "None", ""):
            problems.append(f"{f}: down_revision inválido (None/vacío). Esto crea otra raíz y rompe la cadena.")
            continue

        ok_any = True

    assert ok_any, "Migración Stripe encontrada pero con problemas:\n" + "\n".join(problems)
