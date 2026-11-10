from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    city: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    city: str | None = None


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    city: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)