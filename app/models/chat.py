from sqlalchemy import BigInteger, Column, String, Text, DateTime, CHAR, ForeignKey
from sqlalchemy.sql import func

from app.core.db import Base


class ChatSession(Base):
    __tablename__ = "chat_session"

    session_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    title = Column(String(200), nullable=True)
    created_date = Column(DateTime, nullable=False, server_default=func.now())
    created_nm = Column(String(50), nullable=False)
    modified_date = Column(DateTime, nullable=True, onupdate=func.now())
    modified_nm = Column(String(50), nullable=True)
    del_yn = Column(CHAR(1), nullable=False, default="N")


class ChatMessage(Base):
    __tablename__ = "chat_message"

    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("chat_session.session_id"), nullable=False)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    created_date = Column(DateTime, nullable=False, server_default=func.now())
    created_nm = Column(String(50), nullable=False)
    modified_date = Column(DateTime, nullable=True, onupdate=func.now())
    modified_nm = Column(String(50), nullable=True)
    del_yn = Column(CHAR(1), nullable=False, default="N")


class ChatFeedback(Base):
    __tablename__ = "chat_feedback"

    feedback_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("chat_session.session_id"), nullable=False)
    message_id = Column(BigInteger, ForeignKey("chat_message.message_id"), nullable=True)
    feedback = Column(String(10), nullable=False)
    reason = Column(String(100), nullable=True)
    created_date = Column(DateTime, nullable=False, server_default=func.now())
    created_nm = Column(String(50), nullable=False)
    modified_date = Column(DateTime, nullable=True, onupdate=func.now())
    modified_nm = Column(String(50), nullable=True)
    del_yn = Column(CHAR(1), nullable=False, default="N")
