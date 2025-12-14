from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

from app.utils import create_initial_admin
from app.connection import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        create_initial_admin(db)
    finally:
        db.close()
    yield
    print("App shutting down...")

app = FastAPI(lifespan=lifespan)

# Custom OpenAPI to show Bearer Token field in Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Inventory Management API",
        version="1.0.0",
        description="JWT + Role Based Auth",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Routers
from app.Router.admin_routes import router as admin_router
from app.Router.auth_routes import router as auth_router
from app.Router.manager_routes import router as manager_router
from app.Router.user_routes import router as user_router

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(manager_router)
app.include_router(user_router)


