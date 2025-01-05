from fastapi import APIRouter,status,Form,Request
from typing import Annotated
from ..database import db_dependency
from ..schemas import CreateUserModel
from ..utils import hash
from .. import models

router=APIRouter(
    prefix='/users',
    tags=['users']
)



#Pages
from fastapi import Request
from fastapi.templating import Jinja2Templates
templates=Jinja2Templates(directory="app/templates")

@router.get("/login-page")
async def render_login_page(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})


  


#endpoints
@router.post("/createuser", name="users_createuser",status_code=status.HTTP_201_CREATED)
async def create_user(name:Annotated[str,Form()],password:Annotated[str,Form()],email:Annotated[str,Form()],request:Request,db:db_dependency):
    try:
        user = CreateUserModel(name=name, email=email, password=password)
        user.password=hash(user.password)
        user_model=models.User(**user.model_dump())
        db.add(user_model)
        db.commit()
        db.refresh(user_model)  
        message = "Signup successful!"
    except Exception as e: 
        message = f"Signup failed: {str(e)}"
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "message": message}
    )  