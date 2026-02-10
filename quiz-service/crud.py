from sqlalchemy.orm import Session
from sqlalchemy import text, func
from .models import Question, AnswerOption, QuizAttempt, AttemptAnswer, AttemptQuestion

def get_random_questions(db: Session, limit: int = 10):
    return (
        db.query(Question)
        .order_by(func.rand())   # MySQL: RAND()
        .limit(limit)
        .all()
    )

def lock_attempt_questions(db: Session, attempt_id: int, questions: list[Question]) -> None:
    # clear if any (para safe kung ma-call twice)
    db.query(AttemptQuestion).filter(AttemptQuestion.attempt_id == attempt_id)\
        .delete(synchronize_session=False)
    
    db.flush()

    db.bulk_save_objects([
        AttemptQuestion(attempt_id=attempt_id, question_id=q.id)
        for q in questions
    ])
    db.commit()

def get_attempt_questions(db: Session, attempt_id: int) -> list[Question]:
    # returns questions in the same set saved for that attempt
    return (
        db.query(Question)
        .join(AttemptQuestion, AttemptQuestion.question_id == Question.id)
        .filter(AttemptQuestion.attempt_id == attempt_id)
        .order_by(AttemptQuestion.id.asc())  # stable order
        .all()
    )

def create_question(db: Session, category: str, text: str):
    q = Question(category=category, text=text)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

def add_option(db: Session, question_id: int, text: str, is_correct: bool):
    opt = AnswerOption(question_id=question_id, text=text, is_correct=is_correct)
    db.add(opt)
    db.commit()
    db.refresh(opt)
    return opt

def list_questions(db: Session):
    return db.query(Question).order_by(Question.id.asc()).all()

def get_options_for_question(db: Session, question_id: int):
    return db.query(AnswerOption).filter(AnswerOption.question_id == question_id).all()

def start_attempt(db: Session, user_id: int) -> QuizAttempt:
    a = QuizAttempt(user_id=user_id, score=0, total=0)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a

def submit_attempt(db: Session, attempt_id: int, answers: list[dict]) -> QuizAttempt:
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise ValueError("Attempt not found")

    # ✅ Get locked questions for this attempt
    locked_qids = {
        qid for (qid,) in (
            db.query(AttemptQuestion.question_id)
            .filter(AttemptQuestion.attempt_id == attempt_id)
            .all()
        )
    }
    if not locked_qids:
        raise ValueError("Attempt has no locked questions")

    # De-duplicate by question_id (keep last answer)
    dedup: dict[int, int] = {}
    for a in answers:
        qid = int(a["question_id"])
        oid = int(a["selected_option_id"])
        if qid in locked_qids:   # ✅ only accept answers from locked set
            dedup[qid] = oid

    # ✅ STRICT: must answer ALL locked questions
    if len(dedup) != len(locked_qids):
        missing = len(locked_qids) - len(dedup)
        raise ValueError(f"Please answer all questions before submitting. Missing: {missing}")

    # Clear old answers (safe even if re-submit)
    db.query(AttemptAnswer).filter(AttemptAnswer.attempt_id == attempt_id) \
        .delete(synchronize_session=False)

    score = 0
    for qid, selected_opt_id in dedup.items():
        opt = db.query(AnswerOption).filter(
            AnswerOption.id == selected_opt_id,
            AnswerOption.question_id == qid,
        ).first()

        # (optional) if selected option is invalid for that question
        if not opt:
            raise ValueError("Invalid option selected")

        is_correct = bool(opt.is_correct)
        if is_correct:
            score += 1

        db.add(AttemptAnswer(
            attempt_id=attempt_id,
            question_id=qid,
            selected_option_id=selected_opt_id,
            is_correct=is_correct
        ))

    attempt.score = score
    attempt.total = len(locked_qids)
    db.commit()
    db.refresh(attempt)
    return attempt

def category_breakdown(db: Session, attempt_id: int) -> dict:
    rows = db.execute(
        text("""
        SELECT q.category, SUM(CASE WHEN aa.is_correct THEN 1 ELSE 0 END) AS correct
        FROM attempt_answer aa
        JOIN question q ON q.id = aa.question_id
        WHERE aa.attempt_id = :aid
        GROUP BY q.category
        """),
        {"aid": attempt_id},
    ).fetchall()

    out = {"comsci": 0, "it": 0, "is": 0, "btvted": 0}
    for cat, correct in rows:
        if cat in out:
            out[cat] = int(correct or 0)
    return out