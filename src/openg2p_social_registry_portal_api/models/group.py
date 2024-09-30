from typing import List, Optional

from pydantic import BaseModel, ConfigDict

class GroupMember(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    phone: str
    birthdate:  Optional[str] = None
    gender:  Optional[str] = None
    company_id: int=1
    

class GroupDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    name: str
    email: str
    phone: str
    kind: str
    registration_date: str
    address: str
    members: List[GroupMember]

class GroupUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    members: List[GroupMember]
    removed_members: List[int] = []  # Add a field for removed members

