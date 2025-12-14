from app.auth.OAuth2 import get_current_user
from fastapi import status, HTTPException, Depends
from app.models import UserRole


def is_inventorymanager(user = Depends(get_current_user)):
    print("Inventory manager called...")
    if user.user_role == UserRole.INVENTORY_MANAGER.value:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Inventory manager can access this route"
        )

def is_admin(user = Depends(get_current_user)):
    print("is_admin CALLED")
    print(f"{user.user_role}")
    if user.user_role == UserRole.ADMIN.value:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin can access this route"
        )

def is_user(user = Depends(get_current_user)):
    if user.user_role == UserRole.USER.value:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin can access this route"
        )