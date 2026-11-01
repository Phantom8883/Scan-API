from fastapi import APIRouter, Depends, status, HTTPException

from ..services.target_service import TargetService
from ..dependencies import require_org_role, 

from uuid import UUID



router = APIRouter(prefix="/organization/{organization_id}/target")

@router.get("/organizations/{organization_id}/targets", status_code=202)
async def get_organization(
    organization_id: UUID,
    service: 
)
