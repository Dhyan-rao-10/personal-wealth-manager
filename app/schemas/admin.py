from pydantic import BaseModel


class AdminUserOut(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    is_admin: bool

    model_config = {"from_attributes": True}
