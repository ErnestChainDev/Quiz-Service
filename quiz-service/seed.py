# quiz_service/seed.py
from __future__ import annotations

from sqlalchemy.orm import Session

from .models import Question, AnswerOption


def _get_or_create_question(db: Session, *, category: str, text: str) -> Question:
    q = (
        db.query(Question)
        .filter(Question.category == category, Question.text == text)
        .first()
    )
    if q:
        return q

    q = Question(category=category, text=text)
    db.add(q)
    db.flush()  # get q.id without committing yet
    return q


def _get_or_create_option(
    db: Session,
    *,
    question_id: int,
    text: str,
    is_correct: bool,
) -> AnswerOption:
    opt = (
        db.query(AnswerOption)
        .filter(AnswerOption.question_id == question_id, AnswerOption.text == text)
        .first()
    )
    if opt:
        # keep correct flag in sync (optional but nice)
        if bool(opt.is_correct) != bool(is_correct):
            opt.is_correct = bool(is_correct)
        return opt

    opt = AnswerOption(question_id=question_id, text=text, is_correct=bool(is_correct))
    db.add(opt)
    return opt


def seed_questions(db: Session) -> dict:
    """
    Idempotent seed:
    - Finds by (category, text) for questions
    - Finds by (question_id, option text) for options
    So you can rerun without duplicates.
    """
    data = [
        # -------------------------
        # BSCS (Computer Science)
        # -------------------------
        {
            "category": "bscs",
            "text": "Which approach is most used to make black-box AI models easier to understand?",
            "options": [
                ("Model compression only", False),
                ("Explainable AI (XAI) methods (e.g., SHAP/LIME)", True),
                ("Increasing dataset size", False),
                ("Overfitting intentionally", False),
            ],
        },
        {
            "category": "bscs",
            "text": "In Natural Language Processing (NLP), which model type mainly drove recent breakthroughs?",
            "options": [
                ("Decision trees", False),
                ("Transformers", True),
                ("k-NN", False),
                ("Naive Bayes only", False),
            ],
        },
        {
            "category": "bscs",
            "text": "Which algorithm is commonly used for shortest paths in weighted graphs with non-negative weights?",
            "options": [
                ("BFS", False),
                ("DFS", False),
                ("Dijkstra’s Algorithm", True),
                ("Kruskal’s Algorithm", False),
            ],
        },
        {
            "category": "bscs",
            "text": "A key ethical issue in AI systems trained on biased data is:",
            "options": [
                ("Faster runtime", False),
                ("Algorithmic unfairness/discrimination", True),
                ("Perfect accuracy", False),
                ("Guaranteed privacy", False),
            ],
        },
        {
            "category": "bscs",
            "text": "What is a typical AI technique used for fraud detection in transactions?",
            "options": [
                ("Random guessing", False),
                ("Anomaly detection using ML", True),
                ("Manual inspection only", False),
                ("Removing encryption", False),
            ],
        },
        {
            "category": "bscs",
            "text": "Autonomous vehicles primarily rely on which AI ability?",
            "options": [
                ("File compression", False),
                ("Perception + decision-making from sensor data", True),
                ("Database normalization", False),
                ("Text formatting", False),
            ],
        },
        {
            "category": "bscs",
            "text": "Which is a Divide-and-Conquer algorithm?",
            "options": [
                ("Bubble Sort", False),
                ("Merge Sort", True),
                ("Linear Search", False),
                ("Greedy coin change (always)", False),
            ],
        },
        {
            "category": "bscs",
            "text": "Which best describes a Greedy algorithm?",
            "options": [
                ("Tries all combinations", False),
                ("Chooses the locally best option each step", True),
                ("Always uses recursion", False),
                ("Works only on graphs", False),
            ],
        },
        {
            "category": "bscs",
            "text": "In predictive analytics for business, the ML output is often:",
            "options": [
                ("A random number", False),
                ("A forecast/classification to guide decisions", True),
                ("Only a database schema", False),
                ("A network cable configuration", False),
            ],
        },
        {
            "category": "bscs",
            "text": "The biggest risk of “autonomous weapons” using AI is mainly about:",
            "options": [
                ("Lower battery life", False),
                ("Accountability and ethical responsibility for lethal decisions", True),
                ("Too much storage usage", False),
                ("Slow internet connection", False),
            ],
        },

        # -------------------------
        # BSIT (Information Technology)
        # -------------------------
        {
            "category": "bsit",
            "text": "A strong ransomware defense strategy includes:",
            "options": [
                ("Paying immediately", False),
                ("Regular offline backups + patching + least privilege", True),
                ("Sharing passwords", False),
                ("Disabling updates forever", False),
            ],
        },
        {
            "category": "bsit",
            "text": "A common IoT security problem is:",
            "options": [
                ("Too many monitors", False),
                ("Weak default passwords and unpatched firmware", True),
                ("Too much RAM", False),
                ("Too many USB ports", False),
            ],
        },
        {
            "category": "bsit",
            "text": "How can AI help cybersecurity teams?",
            "options": [
                ("By deleting all logs", False),
                ("By detecting threats/anomalies faster from patterns", True),
                ("By disabling encryption", False),
                ("By removing access controls", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Why is quantum computing a cybersecurity concern?",
            "options": [
                ("It makes Wi-Fi slower", False),
                ("It could break many current public-key encryption schemes", True),
                ("It deletes backups", False),
                ("It prevents cloud usage", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Biometric authentication example:",
            "options": [
                ("CAPTCHA", False),
                ("Fingerprint/Face recognition", True),
                ("Email address", False),
                ("Device name", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Which is a privacy-preserving technique in analytics?",
            "options": [
                ("Posting datasets publicly", False),
                ("Differential privacy", True),
                ("Sharing raw identifiers", False),
                ("Removing passwords only", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Blockchain can help secure storage mainly because it is:",
            "options": [
                ("Always free", False),
                ("Tamper-evident and append-only", True),
                ("Faster than RAM", False),
                ("Offline by default", False),
            ],
        },
        {
            "category": "bsit",
            "text": "A remote work cybersecurity challenge is:",
            "options": [
                ("Too many keyboards", False),
                ("Unsecured home networks and phishing", True),
                ("More monitors", False),
                ("Faster CPUs", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Social engineering prevention strategy:",
            "options": [
                ("Ignore training", False),
                ("Security awareness + verification procedures", True),
                ("Share OTP codes", False),
                ("Use only simple passwords", False),
            ],
        },
        {
            "category": "bsit",
            "text": "A best practice in cloud security is:",
            "options": [
                ("One password for all", False),
                ("IAM least privilege + MFA + logging/monitoring", True),
                ("Disable encryption", False),
                ("Public admin access", False),
            ],
        },

        # -------------------------
        # BSIS (Information System)
        # -------------------------
        {
            "category": "bsis",
            "text": "AI-driven personalized learning systems mainly use data to:",
            "options": [
                ("Replace teachers completely", False),
                ("Adapt content and pace per learner", True),
                ("Remove assessments", False),
                ("Block feedback", False),
            ],
        },
        {
            "category": "bsis",
            "text": "In business, predictive analytics is used to:",
            "options": [
                ("Guess randomly", False),
                ("Forecast trends (sales, churn, demand) using historical data", True),
                ("Hide dashboards", False),
                ("Delete customer data", False),
            ],
        },
        {
            "category": "bsis",
            "text": "Ethical implication of big data use includes:",
            "options": [
                ("Less storage", False),
                ("Privacy risks and potential misuse", True),
                ("No need for consent", False),
                ("Guaranteed fairness", False),
            ],
        },
        {
            "category": "bsis",
            "text": "Big data in personalized marketing often uses:",
            "options": [
                ("Customer segmentation and recommendation models", True),
                ("Manual paper surveys only", False),
                ("Fax machines", False),
                ("Offline-only records", False),
            ],
        },
        {
            "category": "bsis",
            "text": "A system that supports decision-making using visual reports is:",
            "options": [
                ("Compiler", False),
                ("Data visualization/dashboard system", True),
                ("Text editor", False),
                ("Antivirus only", False),
            ],
        },
        {
            "category": "bsis",
            "text": "Blockchain in supply chain management is useful for:",
            "options": [
                ("Making products heavier", False),
                ("Traceability and tamper-evident records", True),
                ("Increasing paperwork", False),
                ("Removing auditing", False),
            ],
        },
        {
            "category": "bsis",
            "text": "A major challenge in multi-cloud management is:",
            "options": [
                ("Too many keyboards", False),
                ("Consistent governance, security, and cost control across providers", True),
                ("Lack of internet", False),
                ("No user accounts", False),
            ],
        },
        {
            "category": "bsis",
            "text": "In e-commerce, cloud disaster recovery is important because it:",
            "options": [
                ("Deletes data faster", False),
                ("Keeps services running after failures", True),
                ("Avoids customer support", False),
                ("Stops scaling", False),
            ],
        },
        {
            "category": "bsis",
            "text": "Fake news detection on social media commonly uses:",
            "options": [
                ("Random posts only", False),
                ("NLP + classification models + network behavior signals", True),
                ("Turning off comments", False),
                ("Manual typing speed tests", False),
            ],
        },
        {
            "category": "bsis",
            "text": "Data protection compliance in IS focuses on:",
            "options": [
                ("Ignoring user consent", False),
                ("Proper collection, storage, access control, and lawful processing", True),
                ("Public passwords", False),
                ("Unlimited sharing", False),
            ],
        },

        # -------------------------
        # BTVTED
        # -------------------------
        {
            "category": "btvted",
            "text": "Gamification in education aims to:",
            "options": [
                ("Remove motivation", False),
                ("Increase engagement using points, badges, challenges", True),
                ("Stop feedback", False),
                ("Reduce participation", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Adaptive learning systems using AI mainly:",
            "options": [
                ("Give the same lesson to everyone", False),
                ("Adjust lessons based on learner performance data", True),
                ("Remove quizzes", False),
                ("Disable analytics", False),
            ],
        },
        {
            "category": "btvted",
            "text": "A benefit of VR in classrooms is:",
            "options": [
                ("Less interaction", False),
                ("Immersive simulations for better understanding", True),
                ("No need for instruction", False),
                ("Lower accessibility automatically", False),
            ],
        },
        {
            "category": "btvted",
            "text": "A big challenge in online learning platforms is:",
            "options": [
                ("Too much chalk", False),
                ("Maintaining student engagement and participation", True),
                ("No devices exist", False),
                ("No internet anywhere", False),
            ],
        },
        {
            "category": "btvted",
            "text": "A good digital literacy initiative should teach learners to:",
            "options": [
                ("Share passwords", False),
                ("Evaluate sources and practice online safety", True),
                ("Ignore privacy settings", False),
                ("Download anything", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Ethics in educational data mining includes:",
            "options": [
                ("Collecting data secretly", False),
                ("Consent, privacy, and responsible use of learner data", True),
                ("Posting grades publicly", False),
                ("Removing security", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Teacher training for tech integration should include:",
            "options": [
                ("Only hardware repair", False),
                ("Pedagogy + tools + classroom management with tech", True),
                ("No lesson planning", False),
                ("Avoiding assessments", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Mobile learning apps can improve performance when they:",
            "options": [
                ("Have no feedback", False),
                ("Provide practice, feedback, and accessible content", True),
                ("Only show ads", False),
                ("Block offline mode always", False),
            ],
        },
        {
            "category": "btvted",
            "text": "AR for historical education is useful because it:",
            "options": [
                ("Deletes history", False),
                ("Adds interactive overlays (3D objects/info) to real environments", True),
                ("Removes visual aids", False),
                ("Makes learning text-only", False),
            ],
        },
        {
            "category": "btvted",
            "text": "In HCI, accessibility means:",
            "options": [
                ("Only design for fast internet", False),
                ("Designing so people with disabilities can effectively use the system", True),
                ("Using small fonts always", False),
                ("Avoiding captions", False),
            ],
        },
    ]

    created_q = 0
    created_opt = 0

    try:
        for item in data:
            q = _get_or_create_question(db, category=item["category"], text=item["text"])
            # options
            before = (
                db.query(AnswerOption)
                .filter(AnswerOption.question_id == q.id)
                .count()
            )
            for opt_text, is_correct in item["options"]:
                _get_or_create_option(
                    db,
                    question_id=q.id,
                    text=opt_text,
                    is_correct=is_correct,
                )
            after = (
                db.query(AnswerOption)
                .filter(AnswerOption.question_id == q.id)
                .count()
            )

            # estimate created counts (idempotent-safe)
            if before == 0:
                created_q += 1
                created_opt += after
            else:
                created_opt += max(0, after - before)

        db.commit()
        return {"ok": True, "created_questions": created_q, "created_options": created_opt}

    except Exception as e:
        db.rollback()
        return {"ok": False, "error": str(e)}