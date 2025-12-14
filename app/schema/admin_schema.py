from pydantic import BaseModel
from typing import List

class RoleAssign(BaseModel):
    user_id: int

class UserInfo(BaseModel):
    user_id: int
    user_name: str
    user_role: str

class UserList(BaseModel):
    userlist: List[UserInfo]


