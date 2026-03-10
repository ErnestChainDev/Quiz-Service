from __future__ import annotations

import os
from typing import cast

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from shared.database import db_dependency
from .crud import (
    add_drag_drop_item,
    add_option,
    cancel_attempt,
    category_breakdown,
    create_question,
    get_attempt_answers,
    get_attempt_questions,
    get_drag_items_for_question,
    get_latest_active_attempt,
    get_options_for_question,
    get_random_questions,
    lock_attempt_questions,
    start_attempt,
    submit_attempt,
    upsert_attempt_answer,
)
from .models import QuizAttempt
from .schemas import (
    AnswerState,
    AttemptProgressOut,
    AttemptStartOut,
    AttemptStatus,
    CancelQuizOut,
    DragDropItemCreateIn,
    DragDropItemOut,
    OptionCreateIn,
    OptionOut,
    QuestionCreateIn,
    QuestionOut,
    SaveAnswerIn,
    SavedAnswerOut,
    SubmitQuizIn,
    SubmitQuizOut,
)

router = APIRouter()
AI_SERVICE_URL = os.getenv(
    "AI_SERVICE_URL",
    "https://ai-recommendation-engine-service-production-ai.up.railway.app",
).rstrip("/")

MIN_RECOMMEND_PERCENT = float(os.getenv("MIN_RECOMMEND_PERCENT", "30"))


def build_router(SessionLocal):
    get_db = db_dependency(SessionLocal)

    def current_user_id(request: Request) -> int:
        x_uid = (request.headers.get("X-User-ID") or "").strip()
        if x_uid:
            try:
                return int(x_uid)
            except ValueError:
                raise HTTPException(status_code=401, detail="Invalid X-User-ID header")

        user = getattr(request.state, "user", None)
        if isinstance(user, dict) and user.get("sub"):
            try:
                return int(user["sub"])
            except (TypeError, ValueError):
                pass

        raise HTTPException(status_code=401, detail="Unauthorized")

    def serialize_question(db: Session, q) -> QuestionOut:
        opts = get_options_for_question(db, q.id)
        drag_items = get_drag_items_for_question(db, q.id)

        return QuestionOut(
            id=q.id,
            category=q.category,
            text=q.text,
            question_type=q.question_type,
            points=q.points,
            time_limit_seconds=q.time_limit_seconds,
            image_url=q.image_url,
            blank_placeholder=q.blank_placeholder,
            options=[
                OptionOut(
                    id=o.id,
                    question_id=o.question_id,
                    text=o.text,
                    display_order=o.display_order,
                )
                for o in opts
            ],
            drag_items=[
                DragDropItemOut(
                    id=d.id,
                    question_id=d.question_id,
                    item_key=d.item_key,
                    item_text=d.item_text,
                    target_key=d.target_key,
                    target_label=d.target_label,
                    display_order=d.display_order,
                )
                for d in drag_items
            ],
        )

    def ensure_attempt_owner(db: Session, attempt_id: int, uid: int) -> QuizAttempt:
        attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        if attempt.user_id != uid:
            raise HTTPException(status_code=403, detail="Forbidden")
        return attempt

    @router.post("/questions", response_model=QuestionOut)
    def create_q(payload: QuestionCreateIn, db: Session = Depends(get_db)):
        q = create_question(
            db=db,
            category=payload.category,
            text=payload.text,
            question_type=payload.question_type,
            points=payload.points,
            time_limit_seconds=payload.time_limit_seconds,
            image_url=payload.image_url,
            blank_placeholder=payload.blank_placeholder,
        )
        return serialize_question(db, q)

    @router.post("/questions/{question_id}/options", response_model=OptionOut)
    def create_opt(question_id: int, payload: OptionCreateIn, db: Session = Depends(get_db)):
        opt = add_option(
            db=db,
            question_id=question_id,
            text=payload.text,
            is_correct=payload.is_correct,
            display_order=payload.display_order,
        )
        return OptionOut(
            id=opt.id,
            question_id=opt.question_id,
            text=opt.text,
            display_order=opt.display_order,
        )

    @router.post("/questions/{question_id}/drag-items", response_model=DragDropItemOut)
    def create_drag_item(
        question_id: int,
        payload: DragDropItemCreateIn,
        db: Session = Depends(get_db),
    ):
        row = add_drag_drop_item(
            db=db,
            question_id=question_id,
            item_key=payload.item_key,
            item_text=payload.item_text,
            target_key=payload.target_key,
            target_label=payload.target_label,
            display_order=payload.display_order,
        )
        return DragDropItemOut.model_validate(row)

    @router.get("/questions", response_model=list[QuestionOut])
    def get_qs(db: Session = Depends(get_db), limit: int = Query(10, ge=1, le=50)):
        qs = get_random_questions(db, limit=limit)
        return [serialize_question(db, q) for q in qs]

    @router.get("/questions/{question_id}/options", response_model=list[OptionOut])
    def get_opts(question_id: int, db: Session = Depends(get_db)):
        opts = get_options_for_question(db, question_id)
        return [
            OptionOut(
                id=o.id,
                question_id=o.question_id,
                text=o.text,
                display_order=o.display_order,
            )
            for o in opts
        ]

    @router.get("/questions/{question_id}/drag-items", response_model=list[DragDropItemOut])
    def get_drag_items(question_id: int, db: Session = Depends(get_db)):
        rows = get_drag_items_for_question(db, question_id)
        return [DragDropItemOut.model_validate(r) for r in rows]

    @router.post("/attempts/start", response_model=AttemptStartOut)
    def start(
        request: Request,
        db: Session = Depends(get_db),
        limit: int = Query(20, ge=1, le=50),
    ):
        uid = current_user_id(request)

        active_attempt = get_latest_active_attempt(db, uid)
        if active_attempt:
            existing_questions = get_attempt_questions(db, active_attempt.id)

            if existing_questions:
                return AttemptStartOut(
                    attempt_id=active_attempt.id,
                    status=cast(AttemptStatus, active_attempt.status),
                )

            qs = get_random_questions(db, limit=limit)

            if len(qs) < limit:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough questions in DB. Need {limit}, found {len(qs)}",
                )

            lock_attempt_questions(db, active_attempt.id, qs)
            db.commit()

            return AttemptStartOut(
                attempt_id=active_attempt.id,
                status=cast(AttemptStatus, active_attempt.status),
            )

        a = start_attempt(db, uid)
        qs = get_random_questions(db, limit=limit)

        if len(qs) < limit:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough questions in DB. Need {limit}, found {len(qs)}",
            )

        lock_attempt_questions(db, a.id, qs)
        db.commit()

        return AttemptStartOut(
            attempt_id=a.id,
            status=cast(AttemptStatus, a.status),
        )

    @router.get("/attempts/{attempt_id}/questions", response_model=list[QuestionOut])
    def attempt_questions(attempt_id: int, request: Request, db: Session = Depends(get_db)):
        uid = current_user_id(request)
        ensure_attempt_owner(db, attempt_id, uid)

        qs = get_attempt_questions(db, attempt_id)
        return [serialize_question(db, q) for q in qs]

    @router.get("/attempts/{attempt_id}/progress", response_model=AttemptProgressOut)
    def attempt_progress(attempt_id: int, request: Request, db: Session = Depends(get_db)):
        uid = current_user_id(request)
        attempt = ensure_attempt_owner(db, attempt_id, uid)

        rows = get_attempt_answers(db, attempt_id)
        saved = []
        for row in rows:
            payload = row.answer_payload or {}
            saved.append(
                SavedAnswerOut(
                    question_id=row.question_id,
                    answer_state=cast(AnswerState, row.answer_state),
                    selected_option_id=payload.get("selected_option_id"),
                    mappings=payload.get("mappings", []),
                    is_correct=bool(row.is_correct),
                    points_earned=int(row.points_earned or 0),
                )
            )

        return AttemptProgressOut(
            attempt_id=attempt.id,
            status=cast(AttemptStatus, attempt.status),
            score=attempt.score,
            total=attempt.total,
            saved_answers=saved,
        )

    @router.put("/attempts/{attempt_id}/answers", response_model=SavedAnswerOut)
    def save_answer(
        attempt_id: int,
        payload: SaveAnswerIn,
        request: Request,
        db: Session = Depends(get_db),
    ):
        uid = current_user_id(request)
        ensure_attempt_owner(db, attempt_id, uid)

        try:
            row = upsert_attempt_answer(db, attempt_id, payload.model_dump())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        answer_payload = row.answer_payload or {}

        return SavedAnswerOut(
            question_id=row.question_id,
            answer_state=cast(AnswerState, row.answer_state),
            selected_option_id=answer_payload.get("selected_option_id"),
            mappings=answer_payload.get("mappings", []),
            is_correct=bool(row.is_correct),
            points_earned=int(row.points_earned or 0),
        )

    @router.post("/attempts/{attempt_id}/cancel", response_model=CancelQuizOut)
    def cancel(
        attempt_id: int,
        request: Request,
        db: Session = Depends(get_db),
    ):
        uid = current_user_id(request)
        ensure_attempt_owner(db, attempt_id, uid)

        try:
            attempt = cancel_attempt(db, attempt_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return CancelQuizOut(
            attempt_id=attempt.id,
            status=cast(AttemptStatus, attempt.status),
            message="Quiz cancelled successfully.",
        )

    @router.post("/attempts/{attempt_id}/submit", response_model=SubmitQuizOut)
    async def submit(
        attempt_id: int,
        payload: SubmitQuizIn,
        request: Request,
        db: Session = Depends(get_db),
    ):
        uid = current_user_id(request)
        ensure_attempt_owner(db, attempt_id, uid)

        try:
            attempt = submit_attempt(
                db,
                attempt_id,
                [a.model_dump() for a in payload.answers],
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        breakdown = category_breakdown(db, attempt_id)

        rec_payload = {
            "user_id": uid,
            "attempt_id": attempt.id,
            "score": attempt.score,
            "total": attempt.total,
            "logic": breakdown.get("bsis", 0),
            "programming": breakdown.get("bscs", 0),
            "networking": breakdown.get("bsit", 0),
            "design": breakdown.get("btvted", 0),
        }

        percent_score = (attempt.score / attempt.total) * 100 if attempt.total > 0 else 0.0

        if percent_score < MIN_RECOMMEND_PERCENT:
            recommendation = {
                "detail": (
                    f"No recommendation available because the score is below "
                    f"the minimum threshold of {MIN_RECOMMEND_PERCENT:.0f}%."
                ),
                "percent_score": round(percent_score, 1),
                "minimum_required_percent": MIN_RECOMMEND_PERCENT,
            }
        else:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    r = await client.post(f"{AI_SERVICE_URL}/ai/recommend", json=rec_payload)

                recommendation = r.json() if 200 <= r.status_code < 300 else {
                    "detail": "AI recommend failed",
                    "status_code": r.status_code,
                    "percent_score": round(percent_score, 1),
                }
            except Exception:
                recommendation = {
                    "detail": "AI service unavailable",
                    "percent_score": round(percent_score, 1),
                }

        return SubmitQuizOut(
            attempt_id=attempt.id,
            status=cast(AttemptStatus, attempt.status),
            score=attempt.score,
            total=attempt.total,
            recommendation=recommendation,
        )

    return router