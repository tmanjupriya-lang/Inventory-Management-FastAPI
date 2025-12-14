from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import UserTable, RefreshTokenTable
from app.connection import get_db
from app.schema.auth_schema import UserLogin, Token, UserOut, UserCreate, RefreshTokenRequest
from app.schema.common_schema import MessageOut
from app.utils import verify_password, hash_password, validate_password_strength
from app.auth.OAuth2 import create_jwt_token, create_refresh_token, get_current_user, verify_refresh_token
from app.Logger.logger import logger

# Route for User Registration and User Login
router = APIRouter(prefix="/auth", tags=["Authentication"])

# User Login route
@router.post("/login", response_model=Token)
def user_login(data: UserLogin, db: Session = Depends(get_db)):
    logger.info("User attempting to login...")
    try:
        user = db.query(UserTable).filter(UserTable.user_name == data.user_name).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(data.password, user.password):
            raise HTTPException(status_code=403, detail="Invalid password")

        logger.info(f"User {user.user_id} authenticated successfully. Generating tokens.")
        jwt_token = create_jwt_token(data={"user_id": user.user_id, "user_role": user.user_role})
        refresh_token = create_refresh_token(data={"user_id": user.user_id, "user_role": user.user_role})

        return {
            "access_token": jwt_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Error occurred during login: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# User Registration route
@router.post("/register", response_model=UserOut, status_code=201)
def user_registration(data: UserCreate, db: Session = Depends(get_db)):
    logger.info("User registration process started...")
    existing_user = db.query(UserTable).filter(UserTable.user_name == data.user_name).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    logger.info("Validating and hashing the password...")
    validate_password_strength(data.password)
    hashed_pwd = hash_password(data.password)

    new_user = UserTable(
        user_name=data.user_name,
        password=hashed_pwd,
        user_role="user"  
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User {new_user.user_id} registered successfully.")
    return new_user

@router.post("/refresh",response_model=Token)
def refresh_access_token(data: RefreshTokenRequest,
                         db: Session = Depends(get_db)):
    logger.info("Refreshing access token")
    payload = verify_refresh_token(data.refresh_token)

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(UserTable).filter(UserTable.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_token = db.query(RefreshTokenTable).filter(
        RefreshTokenTable.user_id == user_id,
        RefreshTokenTable.token == data.refresh_token
    ).first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token is invalid or expired")

    new_access_token = create_jwt_token({"user_id": user.user_id,
                                            "user_role": user.user_role})

    new_refresh_token = create_refresh_token({"user_id": user.user_id})
    db_token.token = new_refresh_token
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


# User Logout route
@router.post("/logout", response_model=MessageOut)
def logout_user(current_user=Depends(get_current_user),
                db: Session = Depends(get_db)):
    logger.info(f"User {current_user.user_id} is logging out")

    # Delete refresh token from DB
    db.query(RefreshTokenTable).filter(
        RefreshTokenTable.user_id == current_user.user_id
    ).delete()

    db.commit()
    logger.info(f"User {current_user.user_id} logged out successfully.")
    return {"message": "Logged out successfully"}