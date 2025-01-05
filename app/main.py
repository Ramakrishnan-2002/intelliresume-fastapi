from fastapi import FastAPI,status,Request,Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine
from fastapi.middleware.cors import CORSMiddleware
from .routers import home, user,auth,chat,resume

app=FastAPI()

origins=["*"] #we can specify which domain we can use 

 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all (bind=engine)
app.mount("/static",StaticFiles(directory="app/static"),name="static")

@app.get("/")
async def test(request:Request,response:Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return RedirectResponse(url="/users/login-page",status_code=status.HTTP_302_FOUND)


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(home.router)
app.include_router(chat.router) 
app.include_router(resume.router)