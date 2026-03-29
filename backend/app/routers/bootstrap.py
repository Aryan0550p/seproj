from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.deps import require_role
from app.models import User
from app.services.demo_seed import reset_company_data, seed_company_demo_data

router = APIRouter()


def _load_sample_data(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    return seed_company_demo_data(session, current_user)


def _reset_company_data(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    return reset_company_data(session, current_user.company_id, keep_admin_user_id=current_user.id)


@router.post("/load-sample-data")
def load_sample_data(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    return _load_sample_data(session, current_user)


@router.post("/reset-company-data")
def reset_company_data_endpoint(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    return _reset_company_data(session, current_user)


@router.post("/seed", include_in_schema=False)
def seed_demo_compat(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    return _load_sample_data(session, current_user)


@router.post("/reset", include_in_schema=False)
def reset_demo_compat(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    return _reset_company_data(session, current_user)
