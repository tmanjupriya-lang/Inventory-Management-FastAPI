from sqlalchemy.orm import Session
from app.connection import get_db
from fastapi import HTTPException, APIRouter, Depends, Query
from app.auth.permission import is_admin
from app.models import UserRole, UserTable
from app.schema.admin_schema import RoleAssign, UserList
from app.Logger.logger import logger
from app.utils import paginate_query

# RBAC - Admin control routes
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# Assigning Role of Admin to the User
@router.patch("/assign-role")
def assign_role(data: RoleAssign, db: Session = Depends(get_db), admin_user=Depends(is_admin)):
    logger.info(f"Admin {admin_user.user_id} is updating the role of user {data.user_id}")
    user = db.query(UserTable).filter(UserTable.user_id == data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.user_role == UserRole.ADMIN.value:
        raise HTTPException(status_code=400, detail="Cannot modify another admin")

    user.user_role = UserRole.ADMIN.value
    db.commit()
    db.refresh(user)
    logger.info(f"The role of user {user.user_id} updated as Admin by Admin {admin_user.user_id}")
    return {"message": f"Role updated to {UserRole.ADMIN} for user {user.user_name}"}


# Assigning Role of Inventory Manager to the User
@router.patch("/create-inventory-manager")
def create_inventory_manager(data: RoleAssign, db: Session = Depends(get_db), admin_user=Depends(is_admin)):
    logger.info(f"Admin {admin_user.user_id} is updating the role of user {data.user_id}")
    user = db.query(UserTable).filter(UserTable.user_id == data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.user_role == UserRole.ADMIN.value:
        raise HTTPException(status_code=400, detail="Cannot modify or downgrade an admin")

    user.user_role = UserRole.INVENTORY_MANAGER.value
    db.commit()
    db.refresh(user)
    logger.info(f"The role of user {user.user_id} updated as Inventory Manager by Admin {admin_user.user_id}")
    return {"message": f"Role updated to {UserRole.INVENTORY_MANAGER} for user {user.user_name}"}


# Admin viewing users
@router.get("/view-users", response_model=UserList)
def view_users(db: Session = Depends(get_db),
               page: int = Query(1, ge=1),
               limit: int = Query(10, ge=1, le=100)):
    logger.info("Admin viewing the users in the table")
    query = db.query(UserTable)
    users = paginate_query(query, page, limit)

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    logger.info(f"Total {len(users)} users fetched by admin on page {page}")
    return {"userlist": users}
