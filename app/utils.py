from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import UserTable, ProductTable
from app.connection import get_db
from email.message import EmailMessage
import os, re , smtplib


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_initial_admin(db : Session):
    admin_exists = db.query(UserTable).filter(UserTable.user_name == "Admin").first()
    if not admin_exists:
        admin = UserTable(user_name = "Admin", password = hash_password("admin@123"),user_role = "Admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Initial admin created successfully!")
    else:
        print("Admin already exists — skipping creation.")

def send_email_alert(subject: str, body: str, to_email: str):
    sender_email = os.getenv("SENDER_EMAIL")        
    sender_pass = os.getenv("SENDER_APP_PASSWORD")  

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_pass)
        smtp.send_message(msg)

    print("Alert email sent successfully!")

def lowstock_alert(db: Session):
    products = db.query(ProductTable).all()
    for product in products:
        if product.product_stockqty < 5:
            subject = f"Low Stock Alert: {product.product_name}"
            body = f"""
            Hello Admin,
            
            The stock for product '{product.product_name}' is running low.
            Current quantity: {product.product_stockqty}
            
            Please restock soon to avoid unavailability.
            
            Regards,
            Inventory System
            """
            send_email_alert(subject, body, "your_email@gmail.com")  # your receiver mail id

            print(f"Alert sent for {product.product_name}")

def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must include at least one uppercase letter"
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must include at least one lowercase letter"
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must include at least one number"
        )
    if not re.search(r"[@$!%*?&]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must include at least one special character (@, $, !, %, *, ?, &)"
        )

def paginate_query(query, page: int, limit: int):
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()



