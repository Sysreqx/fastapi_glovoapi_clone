from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app import models
from app.database import engine

from app.routers import auth, users, notifications, orders
from app.routers.auth import *

description = """
"""

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Glovo Partners API",
        version="",
        description=description,
        contact={
            "email": "partner.integrationseu@glovoapp.com",
        },
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://api-docs.glovoapp.com/partners/img/logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(notifications.router)
app.include_router(users.router)


@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise token_exception()

    token_expires = timedelta(minutes=30)

    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    return {"token": token}
