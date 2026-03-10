# quiz_service/main.py
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from shared.database import Base, build_mysql_url, make_engine, make_session_factory
from .routes import build_router

load_dotenv()

app = FastAPI(title="Quiz Service", version="2.0.0")

db_url = build_mysql_url(
    host=os.environ["MYSQLHOST"],
    port=os.environ["MYSQLPORT"],
    user=os.environ["MYSQLUSER"],
    password=os.environ["MYSQLPASSWORD"],
    db=os.environ["MYSQLDATABASE"],
)

engine = make_engine(db_url)
SessionLocal = make_session_factory(engine)

# NOTE:
# create_all() only creates missing tables.
# It will NOT alter old existing columns/tables.
Base.metadata.create_all(bind=engine)

app.include_router(build_router(SessionLocal), prefix="/quiz", tags=["quiz"])


@app.get("/health")
def health():
    return {"status": "healthy", "service": "quiz-service"}


@app.on_event("startup")
def seed_on_startup():
    """
    - Default: seed ONLY if no questions exist yet
    - Force seed with: SEED_QUESTIONS=1
    """
    from .seed import seed_questions
    from .models import Question

    force = os.getenv("SEED_QUESTIONS", "0") == "1"

    db = SessionLocal()
    try:
        has_any = db.query(Question.id).first() is not None
        if force or not has_any:
            result = seed_questions(db)
            print("SEED RESULT:", result)
    finally:
        db.close()