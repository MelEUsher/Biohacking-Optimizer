from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.database import get_session
from api.models.db_models import DailyEntry, User
from api.models.schemas import EntryCreate, EntryResponse

router = APIRouter(prefix="/entries", tags=["entries"])


def _get_entry_or_404(entry_id: int, db: Session) -> DailyEntry:
    entry = db.query(DailyEntry).filter(DailyEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found",
        )
    return entry


def _ensure_owner(entry: DailyEntry, current_user: User) -> None:
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this entry",
        )


@router.post("", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    payload: EntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> DailyEntry:
    entry = DailyEntry(user_id=current_user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[EntryResponse])
def list_entries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[DailyEntry]:
    return (
        db.query(DailyEntry)
        .filter(DailyEntry.user_id == current_user.id)
        .order_by(DailyEntry.date.asc(), DailyEntry.id.asc())
        .all()
    )


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> DailyEntry:
    entry = _get_entry_or_404(entry_id, db)
    _ensure_owner(entry, current_user)
    return entry


@router.put("/{entry_id}", response_model=EntryResponse)
def update_entry(
    entry_id: int,
    payload: EntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> DailyEntry:
    entry = _get_entry_or_404(entry_id, db)
    _ensure_owner(entry, current_user)

    for field, value in payload.model_dump().items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> Response:
    entry = _get_entry_or_404(entry_id, db)
    _ensure_owner(entry, current_user)

    db.delete(entry)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
