from fastapi import APIRouter
router = APIRouter()

@router.post("/stripe")
def stripe_webhook():
    return {"status": "received"}
