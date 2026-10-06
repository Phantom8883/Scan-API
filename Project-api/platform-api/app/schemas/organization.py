from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):
    name: str


class OrganizationRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str


class OrganizationMembershipRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: UUID
    organization_id: UUID
    role: str