import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from shared.database import db_dependency
from .models import QuizAttempt
from .schemas import (
    QuestionCreateIn, OptionCreateIn,
    QuestionOut, OptionOut,
    AttemptStartOut, SubmitQuizIn, SubmitQuizOut,
)
from .crud import (
    create_question, add_option,
    get_random_questions, get_attempt_questions, lock_attempt_questions,
    get_options_for_question,
    start_attempt, submit_attempt, category_breakdown,
)

router = APIRouter()
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-recommendation-engine:8005").rstrip("/")


def build_router(SessionLocal):
    get_db = db_dependency(SessionLocal)

    def current_user_id(request: Request) -> int:
        # ✅ Preferred: gateway-forwarded identity
        x_uid = (request.headers.get("X-User-ID") or "").strip()
        if x_uid:
            try:
                return int(x_uid)
            except ValueError:
                raise HTTPException(status_code=401, detail="Invalid X-User-ID header")

        # ✅ Fallback: if you ever add auth middleware inside quiz-service
        user = getattr(request.state, "user", None)
        if isinstance(user, dict) and user.get("sub"):
            try:
                return int(user["sub"])
            except (TypeError, ValueError):
                pass

        raise HTTPException(status_code=401, detail="Unauthorized")

    # -------------------------
    # Questions (Admin-ish)
    # -------------------------
    @router.post("/questions", response_model=QuestionOut)
    def create_q(payload: QuestionCreateIn, db: Session = Depends(get_db)):
        return create_question(db, payload.category, payload.text)

    @router.post("/questions/{question_id}/options", response_model=OptionOut)
    def create_opt(question_id: int, payload: OptionCreateIn, db: Session = Depends(get_db)):
        opt = add_option(db, question_id, payload.text, payload.is_correct)
        return OptionOut(id=opt.id, question_id=opt.question_id, text=opt.text)

    # -------------------------
    # Random questions (preview/testing only)
    # -------------------------
    @router.get("/questions", response_model=list[QuestionOut])
    def get_qs(db: Session = Depends(get_db), limit: int = Query(10, ge=1, le=50)):
        return get_random_questions(db, limit=limit)

    @router.get("/questions/{question_id}/options", response_model=list[OptionOut])
    def get_opts(question_id: int, db: Session = Depends(get_db)):
        opts = get_options_for_question(db, question_id)
        return [OptionOut(id=o.id, question_id=o.question_id, text=o.text) for o in opts]

    # -------------------------
    # Attempts (LOCK questions here)
    # -------------------------
    @router.post("/attempts/start", response_model=AttemptStartOut)
    def start(
        request: Request,
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50),
    ):
        uid = current_user_id(request)

        # 1) create attempt
        a = start_attempt(db, uid)

        # 2) pick random questions ONCE
        qs = get_random_questions(db, limit=limit)

        # 3) lock them to this attempt (refresh-safe)
        lock_attempt_questions(db, a.id, qs)

        return AttemptStartOut(attempt_id=a.id)

    # ✅ refresh-safe: always returns same questions
    @router.get("/attempts/{attempt_id}/questions", response_model=list[QuestionOut])
    def attempt_questions(attempt_id: int, request: Request, db: Session = Depends(get_db)):
        uid = current_user_id(request)

        attempt_row = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
        if not attempt_row:
            raise HTTPException(status_code=404, detail="Attempt not found")
        if attempt_row.user_id != uid:
            raise HTTPException(status_code=403, detail="Forbidden")

        return get_attempt_questions(db, attempt_id)

    @router.post("/attempts/{attempt_id}/submit", response_model=SubmitQuizOut)
    async def submit(
        attempt_id: int,
        payload: SubmitQuizIn,
        request: Request,
        db: Session = Depends(get_db),
    ):
        uid = current_user_id(request)

        attempt_row = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
        if not attempt_row:
            raise HTTPException(status_code=404, detail="Attempt not found")
        if attempt_row.user_id != uid:
            raise HTTPException(status_code=403, detail="Forbidden")

        try:
            attempt = submit_attempt(db, attempt_id, [a.model_dump() for a in payload.answers])
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        breakdown = category_breakdown(db, attempt_id)

        rec_payload = {
            "user_id": uid,
            "attempt_id": attempt.id,
            "score": attempt.score,
            "total": attempt.total,
            
            "logic": breakdown["bsis"],
            "programming": breakdown["bscs"],
            "networking": breakdown["bsit"],
            "design": breakdown["btvted"],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(f"{AI_SERVICE_URL}/ai/recommend", json=rec_payload)

            recommendation = r.json() if 200 <= r.status_code < 300 else {
                "detail": "AI recommend failed",
                "status_code": r.status_code,
            }
        except Exception:
            recommendation = {"detail": "AI service unavailable"}

        return SubmitQuizOut(
            attempt_id=attempt.id,
            score=attempt.score,
            total=attempt.total,
            recommendation=recommendation,
        )

    return router