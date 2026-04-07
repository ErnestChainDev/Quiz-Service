from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, text, true
from sqlalchemy.orm import Session

from .models import (
    Question,
    AnswerOption,
    DragDropItem,
    QuizAttempt,
    AttemptAnswer,
    AttemptQuestion,
)


def _get_random_questions_by_type(
    db: Session,
    *,
    question_type: str,
    limit: int,
) -> list[Question]:
    if limit <= 0:
        return []

    return (
        db.query(Question)
        .filter(
            Question.is_active.is_(True),
            Question.question_type == question_type,
        )
        .order_by(func.rand())
        .limit(limit)
        .all()
    )


def get_random_questions(db: Session, limit: int = 10) -> list[Question]:
    """
    Balanced selection by question type.

    Default target for 20:
    - 8 mcq
    - 7 fill_blank_choice
    - 5 drag_drop

    If limit is different, it scales proportionally.
    If one type lacks enough questions, remaining slots are filled
    from other active questions not yet selected.
    """
    if limit <= 0:
        return []

    # preferred mix based on 20-question quiz
    mcq_target = round(limit * 0.40)
    fill_target = round(limit * 0.35)
    drag_target = limit - mcq_target - fill_target

    selected: list[Question] = []
    selected_ids: set[int] = set()

    mcq = _get_random_questions_by_type(db, question_type="mcq", limit=mcq_target)
    fill = _get_random_questions_by_type(
        db,
        question_type="fill_blank_choice",
        limit=fill_target,
    )
    drag = _get_random_questions_by_type(db, question_type="drag_drop", limit=drag_target)

    for bucket in (mcq, fill, drag):
        for q in bucket:
            if q.id not in selected_ids:
                selected.append(q)
                selected_ids.add(q.id)

    remaining = limit - len(selected)
    if remaining > 0:
        extra = (
            db.query(Question)
            .filter(
                Question.is_active.is_(True),
                ~Question.id.in_(selected_ids) if selected_ids else true(),
            )
            .order_by(func.rand())
            .limit(remaining)
            .all()
        )
        for q in extra:
            if q.id not in selected_ids:
                selected.append(q)
                selected_ids.add(q.id)

    # shuffle final list so hindi grouped by type
    if selected:
        ids = [q.id for q in selected]
        shuffled = (
            db.query(Question)
            .filter(Question.id.in_(ids))
            .order_by(func.rand())
            .all()
        )
        return shuffled

    return selected


def lock_attempt_questions(db: Session, attempt_id: int, questions: list[Question]) -> None:
    db.query(AttemptQuestion).filter(AttemptQuestion.attempt_id == attempt_id).delete(
        synchronize_session=False
    )
    db.flush()

    rows = [
        AttemptQuestion(
            attempt_id=attempt_id,
            question_id=q.id,
            order_index=idx,
        )
        for idx, q in enumerate(questions, start=1)
    ]
    db.bulk_save_objects(rows)
    db.flush()


def get_attempt_questions(db: Session, attempt_id: int) -> list[Question]:
    return (
        db.query(Question)
        .join(AttemptQuestion, AttemptQuestion.question_id == Question.id)
        .filter(AttemptQuestion.attempt_id == attempt_id)
        .order_by(AttemptQuestion.order_index.asc(), AttemptQuestion.id.asc())
        .all()
    )


def create_question(
    db: Session,
    category: str,
    text: str,
    question_type: str = "mcq",
    points: int = 1,
    time_limit_seconds: int = 40,
    image_url: str | None = None,
    blank_placeholder: str | None = None,
):
    q = Question(
        category=category,
        text=text,
        question_type=question_type,
        points=points,
        time_limit_seconds=time_limit_seconds,
        image_url=image_url,
        blank_placeholder=blank_placeholder,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def add_option(
    db: Session,
    question_id: int,
    text: str,
    is_correct: bool,
    display_order: int = 0,
):
    opt = AnswerOption(
        question_id=question_id,
        text=text,
        is_correct=is_correct,
        display_order=display_order,
    )
    db.add(opt)
    db.commit()
    db.refresh(opt)
    return opt


def add_drag_drop_item(
    db: Session,
    question_id: int,
    item_key: str,
    item_text: str,
    target_key: str | None,
    target_label: str | None,
    display_order: int = 0,
):
    row = DragDropItem(
        question_id=question_id,
        item_key=item_key,
        item_text=item_text,
        target_key=target_key,
        target_label=target_label,
        display_order=display_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_questions(db: Session):
    return db.query(Question).order_by(Question.id.asc()).all()


def get_options_for_question(db: Session, question_id: int):
    return (
        db.query(AnswerOption)
        .filter(AnswerOption.question_id == question_id)
        .order_by(AnswerOption.display_order.asc(), AnswerOption.id.asc())
        .all()
    )


def get_drag_items_for_question(db: Session, question_id: int):
    return (
        db.query(DragDropItem)
        .filter(DragDropItem.question_id == question_id)
        .order_by(DragDropItem.display_order.asc(), DragDropItem.id.asc())
        .all()
    )


def get_latest_active_attempt(db: Session, user_id: int) -> QuizAttempt | None:
    return (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.status == "in_progress",
        )
        .order_by(QuizAttempt.id.desc())
        .first()
    )


def get_latest_completed_attempt(db: Session, user_id: int) -> QuizAttempt | None:
    return (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.status == "completed",
        )
        .order_by(QuizAttempt.id.desc())
        .first()
    )


def start_attempt(db: Session, user_id: int) -> QuizAttempt:
    a = QuizAttempt(
        user_id=user_id,
        score=0,
        total=0,
        status="in_progress",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def get_attempt_or_raise(db: Session, attempt_id: int) -> QuizAttempt:
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise ValueError("Attempt not found")
    return attempt


def get_locked_question_ids(db: Session, attempt_id: int) -> list[int]:
    rows = (
        db.query(AttemptQuestion.question_id)
        .filter(AttemptQuestion.attempt_id == attempt_id)
        .order_by(AttemptQuestion.order_index.asc())
        .all()
    )
    return [qid for (qid,) in rows]


def upsert_attempt_answer(db: Session, attempt_id: int, answer: dict) -> AttemptAnswer:
    attempt = get_attempt_or_raise(db, attempt_id)
    if attempt.status != "in_progress":
        raise ValueError("This attempt is no longer active")

    question_id = int(answer["question_id"])
    answer_state = answer.get("answer_state", "answered")

    locked_qids = set(get_locked_question_ids(db, attempt_id))
    if question_id not in locked_qids:
        raise ValueError("Question is not part of this attempt")

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError("Question not found")

    row = (
        db.query(AttemptAnswer)
        .filter(
            AttemptAnswer.attempt_id == attempt_id,
            AttemptAnswer.question_id == question_id,
        )
        .first()
    )
    if not row:
        row = AttemptAnswer(attempt_id=attempt_id, question_id=question_id)
        db.add(row)

    points_earned = 0
    is_correct = False
    payload = None

    if answer_state == "missed":
        payload = None
        points_earned = 0
        is_correct = False

    elif question.question_type in ("mcq", "fill_blank_choice"):
        selected_option_id = answer.get("selected_option_id")
        if not selected_option_id:
            answer_state = "unanswered"
            payload = None
            points_earned = 0
            is_correct = False
        else:
            opt = (
                db.query(AnswerOption)
                .filter(
                    AnswerOption.id == int(selected_option_id),
                    AnswerOption.question_id == question_id,
                )
                .first()
            )
            if not opt:
                raise ValueError("Invalid option selected")

            payload = {"selected_option_id": int(selected_option_id)}
            is_correct = bool(opt.is_correct)
            points_earned = int(question.points if is_correct else 0)

    elif question.question_type == "drag_drop":
        mappings = answer.get("mappings", []) or []
        payload = {"mappings": mappings}

        correct_items = get_drag_items_for_question(db, question_id)
        correct_map = {
            item.item_key: item.target_key
            for item in correct_items
            if item.target_key is not None
        }

        submitted_map = {
            m["item_key"]: m["target_key"]
            for m in mappings
            if "item_key" in m and m["target_key"] is not None
        }

        points_earned = 0
        for item_key, correct_target in correct_map.items():
            if submitted_map.get(item_key) == correct_target:
                points_earned += 1

        is_correct = points_earned == len(correct_map) and len(correct_map) > 0

        if not mappings:
            answer_state = "unanswered"

    else:
        raise ValueError("Unsupported question type")

    row.answer_state = answer_state
    row.answer_payload = payload
    row.is_correct = is_correct
    row.points_earned = points_earned
    row.answered_at = datetime.utcnow() if answer_state == "answered" else None

    db.commit()
    db.refresh(row)
    return row


def get_attempt_answers(db: Session, attempt_id: int) -> list[AttemptAnswer]:
    return (
        db.query(AttemptAnswer)
        .filter(AttemptAnswer.attempt_id == attempt_id)
        .order_by(AttemptAnswer.question_id.asc())
        .all()
    )


def compute_attempt_totals(db: Session, attempt_id: int) -> tuple[int, int]:
    # get all questions for this attempt
    questions = get_attempt_questions(db, attempt_id)

    if not questions:
        return 0, 0

    question_ids = [q.id for q in questions]

    # 🔥 fetch ALL drag items in ONE query (optimized)
    drag_items = (
        db.query(DragDropItem)
        .filter(DragDropItem.question_id.in_(question_ids))
        .all()
    )

    # 🔥 group drag items by question_id (ignore distractors)
    drag_map: dict[int, list[DragDropItem]] = {}
    for item in drag_items:
        if item.target_key is None:
            continue  # ignore distractor
        drag_map.setdefault(item.question_id, []).append(item)

    # 🔥 compute total score
    total = 0
    for q in questions:
        if q.question_type == "drag_drop":
            total += len(drag_map.get(q.id, []))  # count only valid matches
        else:
            total += q.points

    # 🔥 compute earned score
    answers = get_attempt_answers(db, attempt_id)
    score = sum(int(a.points_earned or 0) for a in answers)

    return score, total


def submit_attempt(db: Session, attempt_id: int, answers: list[dict]) -> QuizAttempt:
    attempt = get_attempt_or_raise(db, attempt_id)
    if attempt.status != "in_progress":
        raise ValueError("Attempt is already finished")

    locked_qids = get_locked_question_ids(db, attempt_id)
    if not locked_qids:
        raise ValueError("Attempt has no locked questions")

    for answer in answers:
        upsert_attempt_answer(db, attempt_id, answer)

    existing = {
        row.question_id: row
        for row in get_attempt_answers(db, attempt_id)
    }

    for qid in locked_qids:
        if qid not in existing:
            db.add(
                AttemptAnswer(
                    attempt_id=attempt_id,
                    question_id=qid,
                    answer_state="unanswered",
                    answer_payload=None,
                    is_correct=False,
                    points_earned=0,
                    answered_at=None,
                )
            )

    db.commit()

    score, total = compute_attempt_totals(db, attempt_id)
    attempt.score = score
    attempt.total = total
    attempt.status = "completed"
    attempt.submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(attempt)
    return attempt


def cancel_attempt(db: Session, attempt_id: int) -> QuizAttempt:
    attempt = get_attempt_or_raise(db, attempt_id)
    if attempt.status != "in_progress":
        raise ValueError("Only active attempts can be cancelled")

    score, total = compute_attempt_totals(db, attempt_id)
    attempt.score = score
    attempt.total = total
    attempt.status = "cancelled"
    attempt.cancelled_at = datetime.utcnow()

    db.commit()
    db.refresh(attempt)
    return attempt


def category_breakdown(db: Session, attempt_id: int) -> dict:
    rows = db.execute(
        text("""
        SELECT q.category, COALESCE(SUM(aa.points_earned), 0) AS earned_points
        FROM attempt_answer aa
        JOIN question q ON q.id = aa.question_id
        WHERE aa.attempt_id = :aid
        GROUP BY q.category
        """),
        {"aid": attempt_id},
    ).fetchall()

    out = {"bscs": 0, "bsit": 0, "bsis": 0, "btvted": 0}
    for cat, earned_points in rows:
        if cat in out:
            out[cat] = int(earned_points or 0)
    return out