from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import json

from database import get_db
from models_db import Changelog, User
from routers.users import get_current_user

router = APIRouter(prefix="/changelog", tags=["changelog"])

# --- Schemas ---
class ChangelogCreate(BaseModel):
    version: str
    date: str
    title: str
    description: str
    changes: List[str]
    type: str # major, minor, patch

class ChangelogResponse(BaseModel):
    id: int
    version: str
    date: str
    title: str
    description: str
    changes: List[str]
    type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/", response_model=List[ChangelogResponse])
def get_changelog(db: Session = Depends(get_db)):
    """
    Get all changelog entries, sorted by created_at desc (or version if we parse it).
    For simplicity, sorting by date/id desc.
    """
    logs = db.query(Changelog).order_by(Changelog.id.desc()).all()
    
    # Parse JSON string back to list for response
    results = []
    for log in logs:
        changes_list = []
        try:
            if log.changes:
                changes_list = json.loads(log.changes)
        except Exception:
            pass
            
        results.append(ChangelogResponse(
            id=log.id,
            version=log.version,
            date=log.date,
            title=log.title,
            description=log.description,
            changes=changes_list,
            type=log.type,
            created_at=log.created_at
        ))
    return results

@router.post("/", response_model=ChangelogResponse)
def create_changelog_entry(
    entry: ChangelogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Create a new changelog entry.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin requires")

    # Check version uniqueness
    existing = db.query(Changelog).filter(Changelog.version == entry.version).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Version {entry.version} already exists")

    new_log = Changelog(
        version=entry.version,
        date=entry.date,
        title=entry.title,
        description=entry.description,
        changes=json.dumps(entry.changes),
        type=entry.type
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return ChangelogResponse(
        id=new_log.id,
        version=new_log.version,
        date=new_log.date,
        title=new_log.title,
        description=new_log.description,
        changes=entry.changes,
        type=new_log.type,
        created_at=new_log.created_at
    )

@router.delete("/{version}")
def delete_changelog_entry(
    version: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin only: Delete a changelog entry by version.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin requires")

    log = db.query(Changelog).filter(Changelog.version == version).first()
    if not log:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(log)
    db.commit()
    
    return {"status": "deleted", "version": version}
