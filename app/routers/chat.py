from datetime import date, datetime

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import (
    FaqCategoryItem,
    MessageCreateRequest,
    MessageItem,
    SessionCreateRequest,
    SessionListItem,
    SessionResponse,
    TopicItem,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])

MESSAGE_MAX_LENGTH = 500

TOPICS = [
    TopicItem(topic_id="fund_consult", label="목돈상담"),
    TopicItem(topic_id="savings_subscription", label="적금청약질문"),
    TopicItem(topic_id="policy_terms", label="정책용어"),
    TopicItem(topic_id="free_input", label="자유입력"),
]

FAQ_CATEGORIES = [
    FaqCategoryItem(category_id="savings", label="적금"),
    FaqCategoryItem(category_id="subscription", label="청약"),
    FaqCategoryItem(category_id="deposit", label="예금"),
    FaqCategoryItem(category_id="investment", label="투자"),
]


# CHAT-002: 대화 세션 관리 API
@router.post("/session", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest, db: Session = Depends(get_db)):
    today_session = (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == payload.user_id,
            ChatSession.del_yn == "N",
            func.date(ChatSession.created_date) == date.today(),
        )
        .order_by(ChatSession.created_date.desc())
        .first()
    )
    if today_session:
        return SessionResponse(
            session_id=today_session.session_id,
            user_id=today_session.user_id,
            title=today_session.title,
            created_date=today_session.created_date,
            is_new=False,
        )

    new_session = ChatSession(
        user_id=payload.user_id,
        title=payload.title,
        created_date=datetime.now(),
        created_nm=str(payload.user_id),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return SessionResponse(
        session_id=new_session.session_id,
        user_id=new_session.user_id,
        title=new_session.title,
        created_date=new_session.created_date,
        is_new=True,
    )


# CHAT-003: 대화 히스토리 저장/조회 API
@router.get("/sessions", response_model=List[SessionListItem])
def list_sessions(user_id: int, db: Session = Depends(get_db)):  # TODO: JWT 연동 후 query param 대신 토큰에서 추출
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id, ChatSession.del_yn == "N")
        .order_by(ChatSession.created_date.desc())
        .all()
    )
    return sessions


@router.get("/history/{session_id}", response_model=List[MessageItem])
def get_history(session_id: int, db: Session = Depends(get_db)):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.session_id == session_id, ChatSession.del_yn == "N")
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.del_yn == "N")
        .order_by(ChatMessage.created_date.asc())
        .all()
    )
    return messages


# CHAT-004: 사용자 질문 입력 처리
@router.post("/message", response_model=MessageItem)
def send_message(payload: MessageCreateRequest, db: Session = Depends(get_db)):
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="질문을 입력해주세요")
    if len(content) > MESSAGE_MAX_LENGTH:
        raise HTTPException(status_code=400, detail=f"질문은 {MESSAGE_MAX_LENGTH}자 이내로 입력해주세요")

    session = (
        db.query(ChatSession)
        .filter(ChatSession.session_id == payload.session_id, ChatSession.del_yn == "N")
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    new_message = ChatMessage(
        session_id=payload.session_id,
        role="user",
        content=content,
        created_date=datetime.now(),
        created_nm=str(session.user_id),
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


# CHAT-005: 초기 카테고리 메뉴 및 FAQ/상품/용어
@router.get("/topics", response_model=List[TopicItem])
def get_topics():
    return TOPICS


@router.get("/faq-categories", response_model=List[FaqCategoryItem])
def get_faq_categories():
    return FAQ_CATEGORIES


@router.get("/products")
def list_products():
    raise NotImplementedError


@router.get("/products/{name}")
def get_product(name: str):
    raise NotImplementedError


@router.get("/glossary")
def list_glossary():
    raise NotImplementedError


@router.get("/glossary/{term}")
def get_glossary_term(term: str):
    raise NotImplementedError


# CHAT-006: 답변 만족도 피드백 저장 API
@router.post("/feedback")
def create_feedback():
    raise NotImplementedError


# RAG-009: 답변 관련 콘텐츠 추천
@router.get("/recommend/{message_id}")
def get_recommendation(message_id: int):
    raise NotImplementedError
