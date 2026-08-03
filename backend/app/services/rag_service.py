"""
The RAG query pipeline (Lessons 5-6, wired together):
embed question -> retrieve (+ confidence threshold) -> build prompt
with context + sliding-window history -> generate -> detect refusal
-> log to Unknown Question Queue if unanswered -> return with sources.
"""

import uuid
import json

from sqlalchemy.orm import Session

from app.config import settings
from app.models.chat import ChatMessage
from app.models.unknown_question import UnknownQuestion
from app.services import vector_store
from app.services.llm_service import embed_text, generate_chat_reply

REFUSAL_PHRASE = "I don't have that information yet - I've flagged this for the CR to review."

SLIDING_WINDOW_SIZE = 6  # last 6 messages (Lesson 6, Strategy 1)


def _build_history_block(db: Session, session_id: uuid.UUID) -> str:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(SLIDING_WINDOW_SIZE)
        .all()
    )
    messages.reverse()  # back to chronological order
    lines = [f"{m.role.capitalize()}: {m.content}" for m in messages]
    return "\n".join(lines)


def _build_context_block(retrieval: dict) -> tuple[str, list[dict]]:
    documents = retrieval["documents"][0]
    metadatas = retrieval["metadatas"][0]
    distances = retrieval["distances"][0]

    context_parts = []
    sources = []
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        if dist > settings.MAX_RELEVANT_DISTANCE:
            continue  # Lesson 6: confidence thresholding - skip weak matches
        if not meta or not doc:
            # Defensive: a chunk with missing/corrupted metadata (e.g. from
            # a prior ID collision before we switched add() -> upsert())
            # should never crash the whole request - just skip it and
            # keep going with whatever chunks ARE usable.
            continue
        source_filename = meta.get("source_filename", "unknown source")
        context_parts.append(f"[Chunk {i+1}] Source: {source_filename}\n{doc}")
        sources.append(
            {"filename": source_filename, "course_code": meta.get("course_code") or None}
        )

    return "\n\n".join(context_parts), sources


def answer_question(
    db: Session,
    user_id: uuid.UUID,
    question: str,
    session_id: uuid.UUID | None,
    course_code: str | None,
) -> dict:
    session_id = session_id or uuid.uuid4()

    # 1. Retrieve
    query_embedding = embed_text(question, task_type="RETRIEVAL_QUERY")
    retrieval = vector_store.query(
        query_embedding=query_embedding,
        top_k=settings.RETRIEVAL_TOP_K,
        course_code=course_code,
    )
    context_block, sources = _build_context_block(retrieval)

    # 2. Build history (sliding window)
    history_block = _build_history_block(db, session_id)

    # 3. Generate
    reply = generate_chat_reply(context_block, history_block, question)

    was_answered = REFUSAL_PHRASE not in reply
    if not was_answered:
        db.add(UnknownQuestion(question=question, asked_by=user_id))
        sources = []  # don't show sources for a refusal

    # 4. Persist conversation turns
    db.add(ChatMessage(session_id=session_id, user_id=user_id, role="user", content=question))
    db.add(
        ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role="assistant",
            content=reply,
            sources=json.dumps(sources),
        )
    )
    db.commit()

    return {
        "reply": reply,
        "session_id": session_id,
        "sources": sources,
        "was_answered_from_knowledge_base": was_answered,
    }
