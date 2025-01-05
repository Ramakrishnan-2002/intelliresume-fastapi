from fastapi import APIRouter, Request, HTTPException, status,Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.OAuth2 import verify_access_token
from ..OAuth2 import get_current_user
from ..schemas import ResumeDetails
from ..database import resume_metadata
from tinydb import Query
import markdown2
import google.generativeai as genai
from ..config import settings
genai.configure(api_key=settings.BARD_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
import html



router = APIRouter(
    tags=['resume']
)
templates = Jinja2Templates(directory="app/templates")




def redirect_to_login():
    redirect_response=RedirectResponse(url="/users/login-page",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    redirect_response.delete_cookie(key="refresh_token")
    redirect_response.delete_cookie(key="auth_token")
    return redirect_response  

@router.get("/resume")
async def dashboard(request:Request):
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
    
        return templates.TemplateResponse("details.html", {"request": request})

    except Exception as e:
        print(f"Error verifying token: {e}")
        return redirect_to_login()
    
def generate(input_data):
    try:
        response = model.generate_content(input_data)    
        generated_text = response.text  
        generated_text = html.unescape(generated_text)
        generated_text = generated_text.replace("**", "<b>").replace("*", "<i>").replace("</i><i>", "").replace("</b><b>", "").replace("<i></i>", "").replace("<b></b>", "")
     
        return markdown2.markdown(generated_text)
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return "Error generating response. Please try again."

@router.post("/resume/details")
async def resume(data:ResumeDetails,request:Request,user=Depends(get_current_user)):
    try:
        cur_skills = f"""Generate skills that are required for this company that I'm currently applying for : 
                            {data.jd},
                            The skillset that I have currently are :
                            {data.skills},
                            Please create a correct skillset for me to put in my skills using the above mentioned skills only for my Resume that I'm creating. NOTE: ONLY WITH THE SKILLS I GAVE YOU THAT I HAD NOT ANYTHING EXTRA. DONT INCLUDE UNNECESSARY TEXTS GIVE ONLY THE DESIRED CONTENT AND ALSO MAKE SURE NOT TO MAKE ANYTHING BOLD OR ITALICS AND GIVE ONLY IN POINTS.
                            """
        upd_skills = generate(cur_skills)
       

        cur_summary = f"""Generate job summary that is required for this company that I'm currently applying for : 
                            {data.jd},
                            The job summary that I have entered is :
                            {data.summary},
                            Please create a professional, 'short job summary' for me to put in my Job Summary/ Job description tab in my Resume that I'm creating. NOTE GIVE ONLY 10 LINES OF DESCRIPTION AND DONT INCLUDE UNNECESSARY TEXTS GIVE ONLY THE DESIRED CONTENT.
                            """
        upd_summary = generate(cur_summary)
        
        
        upd_summary = upd_summary.replace("*", "<b>").replace("</b><b>", "").replace("</b><b>", "").replace("<b></b>", "")

        cur_proj = f"""Generate Project summary that are required for this company that I'm currently applying for : 
                            {data.jd},
                            The Project summary that I have entered is :
                            {data.projects},
                            Please create a professional, project description presumably in points for me to put in my projects that I have worked on in my Resume that I'm creating, also make it emphasizing : MY ROLE IN IT, NEED FOR THIS PROJECT, FUTURE OF THIS PROJECT, HOW THIS AFFECTS THE CURRENT PERIOD AND DONT INCLUDE UNNECESSARY TEXTS GIVE ONLY THE DESIRED CONTENT.
                            """
        upd_proj = generate(cur_proj)
        
        user_id=user.id
        User = Query()
        resume_metadata.clear_cache()
        resume_metadata.remove(User.user_id == user_id)

        resume_metadata.insert({'user_id':user_id,'email': data.email, 'name':data.name, 'phone':data.phone, 'location':data.location, 'linkedin':data.linkedin, 'github':data.github, 'summary':upd_summary, 'work':data.work, 'skills':upd_skills, 'education':data.education,
                    'projects':upd_proj, 'certifications':data.certifications})          
        
        try:

            return RedirectResponse(url="/resgen", status_code=302)
        except Exception as e:
            print(f"Error in /resume/details: {e}")
            return JSONResponse(
                content={"detail": "Failed to process resume details."},
                status_code=500
            )

    except:
        return templates.TemplateResponse("details.html",{"request":request} )
    

@router.get("/resgen")
async def test_render(request: Request):
    try:
        token_value = request.cookies.get("access_token")
        if not token_value:
            print("Access token missing in cookies.")
            return redirect_to_login()

        user = verify_access_token(
            token=token_value,
            credential_exception=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        )

        # Fetch resume data
        User = Query()
        obj = resume_metadata.search(User.user_id == user.id )

        if not obj:
            return JSONResponse(
                content={"detail": "Resume data not found."},
                status_code=404
            )

        data = {
            "request": request,
            "name": obj[0]["name"],
            "phone": obj[0]["phone"],
            "location": obj[0]["location"],
            "linkedin": obj[0]["linkedin"],
            "github": obj[0]["github"],
            "email": obj[0]["email"],
            "summary": obj[0]["summary"],
            "work": obj[0]["work"],
            "skills": obj[0]["skills"],
            "education": obj[0]["education"],
            "proj": obj[0]["projects"],
            "cert": obj[0]["certifications"],
        }

        return templates.TemplateResponse("resume.html", data)
    except HTTPException as e:
        print(f"Authentication error: {e}")
        return redirect_to_login()
    except Exception as e:
        print(f"Unexpected error in /resgen: {e}")
        return redirect_to_login()