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

PROFILE_SERVICE_URL = os.getenv(
    "PROFILE_SERVICE_URL",
    "https://profileservice-production-profile.up.railway.app",
).rstrip("/")

MIN_RECOMMEND_PERCENT = float(os.getenv("MIN_RECOMMEND_PERCENT", "30"))


# 🔥 NEW: FETCH PROFILE
async def fetch_profile(user_id: int) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{PROFILE_SERVICE_URL}/profile/by-user/{user_id}"
            )

        if res.status_code == 200:
            data = res.json()
            print("PROFILE:", data)  # debug
            return data

        return {}

    except Exception as e:
        print("PROFILE ERROR:", str(e))
        return {}


def build_router(SessionLocal):
    get_db = db_dependency(SessionLocal)

    def current_user_id(request: Request) -> int:
        x_uid = (request.headers.get("X-User-ID") or "").strip()
        if x_uid:
            return int(x_uid)
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

    @router.post("/attempts/{attempt_id}/submit", response_model=SubmitQuizOut)
    async def submit(
        attempt_id: int,
        payload: SubmitQuizIn,
        request: Request,
        db: Session = Depends(get_db),
    ):
        uid = current_user_id(request)
        ensure_attempt_owner(db, attempt_id, uid)

        # ✅ Submit quiz
        attempt = submit_attempt(
            db,
            attempt_id,
            [a.model_dump() for a in payload.answers],
        )

        breakdown = category_breakdown(db, attempt_id)

        # 🔥 FETCH PROFILE HERE
        profile = await fetch_profile(uid)

        # 🔥 FIXED PAYLOAD
        rec_payload = {
            "user_id": uid,
            "attempt_id": attempt.id,
            "score": attempt.score,
            "total": attempt.total,
            "logic": breakdown.get("bsis", 0),
            "programming": breakdown.get("bscs", 0),
            "networking": breakdown.get("bsit", 0),
            "design": breakdown.get("btvted", 0),

            # ✅ NOW WORKING
            "user_skills": profile.get("skills", []),
            "user_interests": profile.get("interests", []),
            "user_career_goals": profile.get("career_goals", []),
        }

        percent_score = (attempt.score / attempt.total) * 100 if attempt.total > 0 else 0.0

        if percent_score < MIN_RECOMMEND_PERCENT:
            recommendation = {
                "detail": "Score too low for recommendation",
                "percent_score": round(percent_score, 1),
            }
        else:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    r = await client.post(
                        f"{AI_SERVICE_URL}/ai/recommend",
                        json=rec_payload,
                        headers={
                            "X-User-ID": str(uid),  # 🔥 REQUIRED FIX
                        },
                    )

                print("AI STATUS:", r.status_code)
                print("AI RESPONSE:", r.text)

                if 200 <= r.status_code < 300:
                    recommendation = r.json()
                else:
                    recommendation = {
                        "detail": "AI failed",
                        "status_code": r.status_code,
                        "percent_score": round(percent_score, 1),
                    }

            except Exception as e:
                print("AI ERROR:", str(e))
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