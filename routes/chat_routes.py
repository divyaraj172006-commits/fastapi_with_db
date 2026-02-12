from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User
from schemas.chat_schemas import ChatSessionResponse, ChatMessageResponse, ChatMessageCreate
from repositories.chat_repository import create_session, get_user_sessions, get_session, add_message, delete_session, toggle_pin_session
from utils.ai_response import get_completion
from routes.user_routes import get_current_user
from typing import List

router = APIRouter()

@router.get("/chats", response_model=List[ChatSessionResponse])
def get_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all chat sessions for the current user."""
    return get_user_sessions(db, current_user.id)

@router.get("/chats/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get messages for a specific chat session."""
    session = get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.messages

@router.post("/chats", response_model=ChatSessionResponse)
def create_new_chat(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new empty chat session."""
    return create_session(db, current_user.id, "New Chat")

@router.post("/chats/{session_id}/messages", response_model=ChatMessageResponse)
def send_message(session_id: int, message: ChatMessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Send a message to a chat session and get AI response."""
    session = get_session(db, session_id, current_user.id)
    if not session:
        # If session_id is 0 or -1 (new chat), create it? 
        # For now, assume explicit creation or valid ID.
        # Let's handle dynamic creation if frontend sends a special ID, but standard REST usually requires valid ID.
        # Frontend should create session first OR we have a separate endpoint to "start chat".
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 1. Save User Message
    user_msg = add_message(db, session_id, "user", message.content)
    
    # 2. Get AI Response
    try:
        # Simple prompt for now, consistent with previous behavior
        ai_text = get_completion(message.content, "You are a helpful AI assistant.")
    except Exception as e:
        ai_text = f"Error: {str(e)}"

    # 3. Save AI Message
    ai_msg = add_message(db, session_id, "ai", ai_text)
    
    # 4. Update Session Title if it's the first message? 
    # (Optional enhancement: rename "New Chat" to first few words of message)
    if len(session.messages) <= 2:
         session.title = message.content[:30] + "..." if len(message.content) > 30 else message.content
         db.commit()

    return ai_msg

@router.delete("/chats/{session_id}")
def delete_chat(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a chat session."""
    success = delete_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}

@router.put("/chats/{session_id}/pin")
def pin_chat(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Toggle pin status of a chat session."""
    session = toggle_pin_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
