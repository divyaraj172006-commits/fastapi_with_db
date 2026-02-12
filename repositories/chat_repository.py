from sqlalchemy.orm import Session
from models import ChatSession, ChatMessage
from schemas.chat_schemas import ChatSessionCreate
import datetime

def create_session(db: Session, user_id: int, title: str):
    db_session = ChatSession(user_id=user_id, title=title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_user_sessions(db: Session, user_id: int):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()

def get_session(db: Session, session_id: int, user_id: int):
    return db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()

def add_message(db: Session, session_id: int, role: str, content: str):
    db_message = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_session(db: Session, session_id: int, user_id: int):
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False

def toggle_pin_session(db: Session, session_id: int, user_id: int):
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
    if db_session:
        db_session.is_pinned = not db_session.is_pinned
        db.commit()
        db.refresh(db_session)
        return db_session
    return None
