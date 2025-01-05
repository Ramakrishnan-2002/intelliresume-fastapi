from fastapi import APIRouter, HTTPException,status
from fastapi.responses import RedirectResponse
from ..models import User
from app.OAuth2 import verify_access_token
from ..database import db_dependency

router = APIRouter()




#Pages
from fastapi import Request
from fastapi.templating import Jinja2Templates 
templates=Jinja2Templates(directory="app/templates")
 

def redirect_to_login():
    redirect_response=RedirectResponse(url="/users/login-page",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    redirect_response.delete_cookie(key="refresh_token")
    redirect_response.delete_cookie(key="auth_token")
    return redirect_response   

@router.get("/dashboard")
async def dashboard(request:Request,db:db_dependency):
    try:
        # Retrieve and wrap the token from cookies
        token_value = request.cookies.get("access_token")
        if not token_value:
            return redirect_to_login()
        
        # Verify token
        user_id =  verify_access_token(
            token=token_value,
            credential_exception=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        )
        user=db.query(User).filter(User.id==user_id.id).first()
        return templates.TemplateResponse("home.html", {"request": request, "user": user,"username":user.name})

    except Exception as e:
        print(f"Error verifying token: {e}")
        return redirect_to_login()
     
 