from fastapi import APIRouter, Depends
from routers.auth_new import get_current_user

router = APIRouter()

@router.get("/")
def get_settings(user=Depends(get_current_user)):
    return {"status": "ok", "settings": {}}
