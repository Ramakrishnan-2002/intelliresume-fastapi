import google.generativeai as genai
from fastapi import APIRouter, Request, HTTPException, status,Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.OAuth2 import verify_access_token
from app.models import User
from ..database import db_dependency
import logging
from ..OAuth2 import get_current_user
from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure the Gemini API
genai.configure(api_key=settings.BARD_API_KEY)

# Router and template setup
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# In-memory store for chat sessions
chat_sessions = {}

def redirect_to_login():
    redirect_response = RedirectResponse(url="/users/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    redirect_response.delete_cookie(key="refresh_token")
    redirect_response.delete_cookie(key="auth_token")
    return redirect_response

def get_chat_session(session_id):
    """
    Retrieves or initializes a chat session for a given session ID.
    """
    if session_id not in chat_sessions:
        try:
            # Create a new chat session with Gemini
            model = genai.GenerativeModel("gemini-1.5-flash")
            chat_sessions[session_id] = model.start_chat(
                history=[
                    {"role": "model", "parts": "Hi! How can I assist you today?"}
                ]
            )
        except Exception as e:
            logging.error(f"Failed to initialize chat session: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize chat session.")
    return chat_sessions[session_id]

@router.get("/chat")
async def dashboard(request: Request, db: db_dependency):
    try:
        token_value = request.cookies.get("access_token")
        if not token_value:
            return redirect_to_login()
        
        # Verify token
        user_id = verify_access_token(
            token=token_value,
            credential_exception=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        )
        user = db.query(User).filter(User.id == user_id.id).first()
        return templates.TemplateResponse("chat.html", {"request": request, "user": user, "username": user.name})
    except Exception as e:
        logging.error(f"Error verifying token: {e}")
        return redirect_to_login()

@router.post("/chat")
async def chat_endpoint(request: Request,user=Depends(get_current_user)):
    """
    Chat endpoint to handle user messages and provide AI responses.
    """
    try:
        # Extract user message from the request
        data = await request.json()
        user_message = data.get("chat")
        if not user_message:
            raise HTTPException(status_code=400, detail="Chat message is required.")

        # Use client IP as a unique session identifier
        print(user.name)
        session_id = str(user.id)  # Ensure it's a string for compatibility
        logging.info(f"Session ID: {session_id}")
        
        chat_session = get_chat_session(session_id)

        # Send the user's message to Gemini
        response = chat_session.send_message(user_message, stream=True)

        # Collect and stream response chunks
        response_text = "".join(chunk.text for chunk in response)

        # Update the chat history
        chat_session.history.append({"role": "user", "parts": user_message})
        chat_session.history.append({"role": "model", "parts": response_text})

        # Return the bot's response
        return JSONResponse({"bot": response_text})

    except Exception as e:
        logging.error(f"Error during chat processing: {e}")
        return JSONResponse({"error": f"An error occurred: {str(e)}"}, status_code=500)
