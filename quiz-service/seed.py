# quiz_service/seed.py
from __future__ import annotations

from sqlalchemy.orm import Session

from .models import Question, AnswerOption, DragDropItem


def _get_or_create_question(
    db: Session,
    *,
    category: str,
    text: str,
    question_type: str = "mcq",
    points: int = 1,
    time_limit_seconds: int = 40,
    image_url: str | None = None,
    blank_placeholder: str | None = None,
) -> Question:
    q = (
        db.query(Question)
        .filter(Question.category == category, Question.text == text)
        .first()
    )
    if q:
        q.question_type = question_type
        q.points = points
        q.time_limit_seconds = time_limit_seconds
        q.image_url = image_url
        q.blank_placeholder = blank_placeholder
        q.is_active = True
        return q

    q = Question(
        category=category,
        text=text,
        question_type=question_type,
        points=points,
        time_limit_seconds=time_limit_seconds,
        image_url=image_url,
        blank_placeholder=blank_placeholder,
        is_active=True,
    )
    db.add(q)
    db.flush()
    return q


def _get_or_create_option(
    db: Session,
    *,
    question_id: int,
    text: str,
    is_correct: bool,
    display_order: int = 0,
) -> AnswerOption:
    opt = (
        db.query(AnswerOption)
        .filter(AnswerOption.question_id == question_id, AnswerOption.text == text)
        .first()
    )
    if opt:
        opt.is_correct = bool(is_correct)
        opt.display_order = display_order
        return opt

    opt = AnswerOption(
        question_id=question_id,
        text=text,
        is_correct=bool(is_correct),
        display_order=display_order,
    )
    db.add(opt)
    return opt


def _get_or_create_drag_item(
    db: Session,
    *,
    question_id: int,
    item_key: str,
    item_text: str,
    target_key: str,
    target_label: str,
    display_order: int = 0,
) -> DragDropItem:
    row = (
        db.query(DragDropItem)
        .filter(
            DragDropItem.question_id == question_id,
            DragDropItem.item_key == item_key,
        )
        .first()
    )
    if row:
        row.item_text = item_text
        row.target_key = target_key
        row.target_label = target_label
        row.display_order = display_order
        return row

    row = DragDropItem(
        question_id=question_id,
        item_key=item_key,
        item_text=item_text,
        target_key=target_key,
        target_label=target_label,
        display_order=display_order,
    )
    db.add(row)
    return row


def _mcq_data() -> list[dict]:
    return [
        # 10 BSCS
        {
            "category": "bscs",
            "text": "Which approach is most used to make black-box AI models easier to understand?",
            "options": [
                ("Model compression only", False),
                ("Explainable AI (XAI) methods such as SHAP/LIME", True),
                ("Increasing dataset size", False),
                ("Overfitting intentionally", False),
            ],
        },
        {
            "category": "bscs",
            "text": "In Natural Language Processing, which model type drove recent breakthroughs?",
            "options": [
                ("Decision trees", False),
                ("Transformers", True),
                ("k-NN only", False),
                ("Naive Bayes only", False),
            ],
        },
        {
            "category": "bscs",
            "text": "Which algorithm is commonly used for shortest paths in weighted graphs with non-negative weights?",
            "options": [
                ("BFS", False),
                ("DFS", False),
                ("Dijkstra's Algorithm", True),
                ("Kruskal's Algorithm", False),
            ],
        },
        {
            "category": "bscs",
            "text": "A key ethical issue in AI systems trained on biased data is:",
            "options": [
                ("Faster runtime", False),
                ("Algorithmic unfairness", True),
                ("Perfect accuracy", False),
                ("Guaranteed privacy", False),
            ],
        },
        {
            "category": "bscs",
            "text": "What is a typical AI technique used for fraud detection?",
            "options": [
                ("Random guessing", False),
                ("Anomaly detection", True),
                ("Manual inspection only", False),
                ("Removing encryption", False),
            ],
        },
        {
            "category": "bscs",
            "text": "Autonomous vehicles mainly rely on which AI ability?",
            "options": [
                ("File compression", False),
                ("Perception and decision-making", True),
                ("Database normalization", False),
                ("Text formatting", False),
            ],
        },
        {
            "category": "bscs",
            "text": "Which is a divide-and-conquer algorithm?",
            "options": [
                ("Bubble Sort", False),
                ("Merge Sort", True),
                ("Linear Search", False),
                ("Selection Sort", False),
            ],
        },
        {
            "category": "bscs",
            "text": "Which best describes a greedy algorithm?",
            "options": [
                ("Tries all combinations", False),
                ("Chooses the locally best option each step", True),
                ("Always uses recursion", False),
                ("Works only on graphs", False),
            ],
        },
        {
            "category": "bscs",
            "text": "In predictive analytics, the output is often:",
            "options": [
                ("A random number", False),
                ("A forecast or classification", True),
                ("Only a schema", False),
                ("A cable configuration", False),
            ],
        },
        {
            "category": "bscs",
            "text": "The biggest risk of autonomous weapons using AI is mainly about:",
            "options": [
                ("Battery life", False),
                ("Accountability for lethal decisions", True),
                ("Storage usage", False),
                ("Slow internet", False),
            ],
        },

        # 10 BSIT
        {
            "category": "bsit",
            "text": "A strong ransomware defense strategy includes:",
            "options": [
                ("Paying immediately", False),
                ("Regular backups, patching, and least privilege", True),
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
                ("By detecting threats faster from patterns", True),
                ("By disabling encryption", False),
                ("By removing access controls", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Why is quantum computing a cybersecurity concern?",
            "options": [
                ("It makes Wi-Fi slower", False),
                ("It could break current public-key encryption", True),
                ("It deletes backups", False),
                ("It prevents cloud use", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Biometric authentication example:",
            "options": [
                ("CAPTCHA", False),
                ("Fingerprint recognition", True),
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
            "text": "Blockchain helps secure storage mainly because it is:",
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
                ("Security awareness and verification procedures", True),
                ("Share OTP codes", False),
                ("Use simple passwords", False),
            ],
        },
        {
            "category": "bsit",
            "text": "A best practice in cloud security is:",
            "options": [
                ("One password for all", False),
                ("Least privilege plus MFA and monitoring", True),
                ("Disable encryption", False),
                ("Public admin access", False),
            ],
        },

        # 10 BSIS / BTVTED mixed
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
                ("Forecast trends using historical data", True),
                ("Hide dashboards", False),
                ("Delete customer data", False),
            ],
        },
        {
            "category": "bsis",
            "text": "Ethical implication of big data use includes:",
            "options": [
                ("Less storage", False),
                ("Privacy risks and misuse", True),
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
                ("Dashboard system", True),
                ("Text editor", False),
                ("Antivirus only", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Gamification in education aims to:",
            "options": [
                ("Remove motivation", False),
                ("Increase engagement using points and badges", True),
                ("Stop feedback", False),
                ("Reduce participation", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Adaptive learning systems using AI mainly:",
            "options": [
                ("Give the same lesson to everyone", False),
                ("Adjust lessons based on learner performance", True),
                ("Remove quizzes", False),
                ("Disable analytics", False),
            ],
        },
        {
            "category": "btvted",
            "text": "A benefit of VR in classrooms is:",
            "options": [
                ("Less interaction", False),
                ("Immersive simulations", True),
                ("No need for instruction", False),
                ("Lower accessibility automatically", False),
            ],
        },
        {
            "category": "btvted",
            "text": "A big challenge in online learning platforms is:",
            "options": [
                ("Too much chalk", False),
                ("Maintaining student engagement", True),
                ("No devices exist", False),
                ("No internet anywhere", False),
            ],
        },
        {
            "category": "btvted",
            "text": "In HCI, accessibility means:",
            "options": [
                ("Only design for fast internet", False),
                ("Designing so people with disabilities can use the system", True),
                ("Using small fonts always", False),
                ("Avoiding captions", False),
            ],
        },
    ]


def _fill_blank_data() -> list[dict]:
    return [
        # 10 BSCS
        {
            "category": "bscs",
            "text": "HTML stands for _____.",
            "blank_placeholder": "_____",
            "options": [
                ("HyperText Markup Language", True),
                ("HighText Machine Language", False),
                ("Home Tool Markup Language", False),
                ("Hyper Transfer Markup Logic", False),
            ],
        },
        {
            "category": "bscs",
            "text": "CSS is mainly used for the _____ of a webpage.",
            "blank_placeholder": "_____",
            "options": [
                ("design", True),
                ("database", False),
                ("server", False),
                ("encryption", False),
            ],
        },
        {
            "category": "bscs",
            "text": "JavaScript is used to add _____ to websites.",
            "blank_placeholder": "_____",
            "options": [
                ("interactivity", True),
                ("cabling", False),
                ("storage racks", False),
                ("cooling", False),
            ],
        },
        {
            "category": "bscs",
            "text": "An algorithm is a step-by-step _____ for solving a problem.",
            "blank_placeholder": "_____",
            "options": [
                ("procedure", True),
                ("monitor", False),
                ("cable", False),
                ("document folder", False),
            ],
        },
        {
            "category": "bscs",
            "text": "The binary number system uses only _____ digits.",
            "blank_placeholder": "_____",
            "options": [
                ("two", True),
                ("three", False),
                ("eight", False),
                ("ten", False),
            ],
        },
        {
            "category": "bscs",
            "text": "A loop repeats a block of _____.",
            "blank_placeholder": "_____",
            "options": [
                ("code", True),
                ("hardware", False),
                ("paint", False),
                ("electricity", False),
            ],
        },
        {
            "category": "bscs",
            "text": "A variable is used to store _____.",
            "blank_placeholder": "_____",
            "options": [
                ("data", True),
                ("chairs", False),
                ("printers only", False),
                ("walls", False),
            ],
        },
        {
            "category": "bscs",
            "text": "In OOP, a class is a blueprint for creating _____.",
            "blank_placeholder": "_____",
            "options": [
                ("objects", True),
                ("routers", False),
                ("spreadsheets", False),
                ("emails", False),
            ],
        },
        {
            "category": "bscs",
            "text": "A database query language commonly used is _____.",
            "blank_placeholder": "_____",
            "options": [
                ("SQL", True),
                ("HTML", False),
                ("CSS", False),
                ("PNG", False),
            ],
        },
        {
            "category": "bscs",
            "text": "The CPU is often called the _____ of the computer.",
            "blank_placeholder": "_____",
            "options": [
                ("brain", True),
                ("window", False),
                ("table", False),
                ("speaker", False),
            ],
        },

        # 10 BSIT
        {
            "category": "bsit",
            "text": "A firewall helps protect a network from _____ access.",
            "blank_placeholder": "_____",
            "options": [
                ("unauthorized", True),
                ("colorful", False),
                ("offline", False),
                ("printed", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Phishing attacks often try to steal user _____.",
            "blank_placeholder": "_____",
            "options": [
                ("credentials", True),
                ("chairs", False),
                ("screens", False),
                ("folders", False),
            ],
        },
        {
            "category": "bsit",
            "text": "MFA stands for Multi-Factor _____.",
            "blank_placeholder": "_____",
            "options": [
                ("Authentication", True),
                ("Automation", False),
                ("Assembly", False),
                ("Activation", False),
            ],
        },
        {
            "category": "bsit",
            "text": "VPN is commonly used to create a secure _____ connection.",
            "blank_placeholder": "_____",
            "options": [
                ("remote", True),
                ("wooden", False),
                ("printed", False),
                ("public speaker", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Malware is software designed to cause _____.",
            "blank_placeholder": "_____",
            "options": [
                ("harm", True),
                ("music", False),
                ("color", False),
                ("animation only", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Strong passwords should be difficult to _____.",
            "blank_placeholder": "_____",
            "options": [
                ("guess", True),
                ("type", False),
                ("store", False),
                ("see", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Cloud computing provides on-demand access to shared _____.",
            "blank_placeholder": "_____",
            "options": [
                ("resources", True),
                ("chalkboards", False),
                ("gardens", False),
                ("paper files only", False),
            ],
        },
        {
            "category": "bsit",
            "text": "An IP address identifies a device on a _____.",
            "blank_placeholder": "_____",
            "options": [
                ("network", True),
                ("book", False),
                ("desk", False),
                ("window", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Encryption helps keep data _____.",
            "blank_placeholder": "_____",
            "options": [
                ("confidential", True),
                ("heavy", False),
                ("loud", False),
                ("public", False),
            ],
        },
        {
            "category": "bsit",
            "text": "Regular backups are important for data _____.",
            "blank_placeholder": "_____",
            "options": [
                ("recovery", True),
                ("painting", False),
                ("typing", False),
                ("advertising", False),
            ],
        },

        # 10 BSIS / BTVTED mixed
        {
            "category": "bsis",
            "text": "MIS stands for Management Information _____.",
            "blank_placeholder": "_____",
            "options": [
                ("System", True),
                ("Signal", False),
                ("Setup", False),
                ("Source", False),
            ],
        },
        {
            "category": "bsis",
            "text": "A DBMS stands for Database Management _____.",
            "blank_placeholder": "_____",
            "options": [
                ("System", True),
                ("Signal", False),
                ("Screen", False),
                ("Sheet", False),
            ],
        },
        {
            "category": "bsis",
            "text": "Dashboards are used to present data in a _____ form.",
            "blank_placeholder": "_____",
            "options": [
                ("visual", True),
                ("wooden", False),
                ("hidden", False),
                ("manual", False),
            ],
        },
        {
            "category": "bsis",
            "text": "Business intelligence helps support better _____.",
            "blank_placeholder": "_____",
            "options": [
                ("decisions", True),
                ("paintings", False),
                ("furniture", False),
                ("songs", False),
            ],
        },
        {
            "category": "bsis",
            "text": "E-commerce refers to buying and selling goods _____.",
            "blank_placeholder": "_____",
            "options": [
                ("online", True),
                ("manually", False),
                ("offline only", False),
                ("by fax only", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Gamification uses badges, points, and _____ to increase engagement.",
            "blank_placeholder": "_____",
            "options": [
                ("challenges", True),
                ("wires", False),
                ("routers", False),
                ("folders", False),
            ],
        },
        {
            "category": "btvted",
            "text": "VR stands for Virtual _____.",
            "blank_placeholder": "_____",
            "options": [
                ("Reality", True),
                ("Resource", False),
                ("Record", False),
                ("Room", False),
            ],
        },
        {
            "category": "btvted",
            "text": "AR stands for Augmented _____.",
            "blank_placeholder": "_____",
            "options": [
                ("Reality", True),
                ("Record", False),
                ("Response", False),
                ("Route", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Digital literacy includes evaluating online _____ carefully.",
            "blank_placeholder": "_____",
            "options": [
                ("sources", True),
                ("chairs", False),
                ("desks", False),
                ("paint", False),
            ],
        },
        {
            "category": "btvted",
            "text": "Online learning platforms should encourage student _____.",
            "blank_placeholder": "_____",
            "options": [
                ("participation", True),
                ("silence", False),
                ("absence", False),
                ("confusion", False),
            ],
        },
    ]


def _drag_drop_data() -> list[dict]:
    return [
        # 5 BSCS
        {
            "category": "bscs",
            "text": "Match the web technology to its function.",
            "drag_items": [
                {
                    "item_key": "html_structure",
                    "item_text": "HTML",
                    "target_key": "slot_structure",
                    "target_label": "Structure",
                    "display_order": 1,
                },
                {
                    "item_key": "css_style",
                    "item_text": "CSS",
                    "target_key": "slot_style",
                    "target_label": "Style",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bscs",
            "text": "Match the programming term to its meaning.",
            "drag_items": [
                {
                    "item_key": "variable_storage",
                    "item_text": "Variable",
                    "target_key": "slot_storage",
                    "target_label": "Stores value",
                    "display_order": 1,
                },
                {
                    "item_key": "loop_repeat",
                    "item_text": "Loop",
                    "target_key": "slot_repeat",
                    "target_label": "Repeats code",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bscs",
            "text": "Match the data structure to its description.",
            "drag_items": [
                {
                    "item_key": "array_ordered",
                    "item_text": "Array",
                    "target_key": "slot_ordered",
                    "target_label": "Ordered collection",
                    "display_order": 1,
                },
                {
                    "item_key": "stack_lifo",
                    "item_text": "Stack",
                    "target_key": "slot_lifo",
                    "target_label": "Last in, first out",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bscs",
            "text": "Match the file extension to its common use.",
            "drag_items": [
                {
                    "item_key": "html_file",
                    "item_text": ".html",
                    "target_key": "slot_webpage",
                    "target_label": "Webpage file",
                    "display_order": 1,
                },
                {
                    "item_key": "py_file",
                    "item_text": ".py",
                    "target_key": "slot_python",
                    "target_label": "Python file",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bscs",
            "text": "Match the algorithm concept to its example.",
            "drag_items": [
                {
                    "item_key": "divide_conquer",
                    "item_text": "Divide and Conquer",
                    "target_key": "slot_mergesort",
                    "target_label": "Merge Sort",
                    "display_order": 1,
                },
                {
                    "item_key": "greedy",
                    "item_text": "Greedy",
                    "target_key": "slot_localbest",
                    "target_label": "Local best choice",
                    "display_order": 2,
                },
            ],
        },

        # 5 BSIT
        {
            "category": "bsit",
            "text": "Match the security term to its description.",
            "drag_items": [
                {
                    "item_key": "firewall_filter",
                    "item_text": "Firewall",
                    "target_key": "slot_filter",
                    "target_label": "Filters traffic",
                    "display_order": 1,
                },
                {
                    "item_key": "antivirus_malware",
                    "item_text": "Antivirus",
                    "target_key": "slot_malware",
                    "target_label": "Detects malware",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bsit",
            "text": "Match the authentication type to its example.",
            "drag_items": [
                {
                    "item_key": "biometric_fingerprint",
                    "item_text": "Biometric",
                    "target_key": "slot_fingerprint",
                    "target_label": "Fingerprint",
                    "display_order": 1,
                },
                {
                    "item_key": "password_secret",
                    "item_text": "Password",
                    "target_key": "slot_secret",
                    "target_label": "Secret phrase",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bsit",
            "text": "Match the network term to its role.",
            "drag_items": [
                {
                    "item_key": "router_routing",
                    "item_text": "Router",
                    "target_key": "slot_route",
                    "target_label": "Routes packets",
                    "display_order": 1,
                },
                {
                    "item_key": "switch_lan",
                    "item_text": "Switch",
                    "target_key": "slot_lan",
                    "target_label": "Connects devices in LAN",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bsit",
            "text": "Match the backup type to its meaning.",
            "drag_items": [
                {
                    "item_key": "full_backup",
                    "item_text": "Full Backup",
                    "target_key": "slot_allfiles",
                    "target_label": "Copies all files",
                    "display_order": 1,
                },
                {
                    "item_key": "incremental_backup",
                    "item_text": "Incremental Backup",
                    "target_key": "slot_changes",
                    "target_label": "Copies recent changes",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bsit",
            "text": "Match the cloud model to its example.",
            "drag_items": [
                {
                    "item_key": "saas_email",
                    "item_text": "SaaS",
                    "target_key": "slot_emailapp",
                    "target_label": "Email app service",
                    "display_order": 1,
                },
                {
                    "item_key": "iaas_server",
                    "item_text": "IaaS",
                    "target_key": "slot_virtualserver",
                    "target_label": "Virtual server",
                    "display_order": 2,
                },
            ],
        },

        # 5 BSIS
        {
            "category": "bsis",
            "text": "Match the business term to its use.",
            "drag_items": [
                {
                    "item_key": "dashboard_visual",
                    "item_text": "Dashboard",
                    "target_key": "slot_visualreports",
                    "target_label": "Visual reports",
                    "display_order": 1,
                },
                {
                    "item_key": "kpi_measure",
                    "item_text": "KPI",
                    "target_key": "slot_performance",
                    "target_label": "Performance measure",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bsis",
            "text": "Match the database term to its meaning.",
            "drag_items": [
                {
                    "item_key": "table_rows",
                    "item_text": "Table",
                    "target_key": "slot_records",
                    "target_label": "Stores records",
                    "display_order": 1,
                },
                {
                    "item_key": "query_request",
                    "item_text": "Query",
                    "target_key": "slot_retrieve",
                    "target_label": "Retrieves data",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bsis",
            "text": "Match the system type to its purpose.",
            "drag_items": [
                {
                    "item_key": "mis_info",
                    "item_text": "MIS",
                    "target_key": "slot_managerinfo",
                    "target_label": "Management information",
                    "display_order": 1,
                },
                {
                    "item_key": "dss_decision",
                    "item_text": "DSS",
                    "target_key": "slot_decisionsupport",
                    "target_label": "Decision support",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bsis",
            "text": "Match the e-commerce term to its role.",
            "drag_items": [
                {
                    "item_key": "cart_order",
                    "item_text": "Shopping Cart",
                    "target_key": "slot_selecteditems",
                    "target_label": "Selected items",
                    "display_order": 1,
                },
                {
                    "item_key": "checkout_payment",
                    "item_text": "Checkout",
                    "target_key": "slot_paymentprocess",
                    "target_label": "Payment process",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "bsis",
            "text": "Match the analytics term to its output.",
            "drag_items": [
                {
                    "item_key": "forecast_future",
                    "item_text": "Forecasting",
                    "target_key": "slot_futuretrend",
                    "target_label": "Future trend",
                    "display_order": 1,
                },
                {
                    "item_key": "segmentation_groups",
                    "item_text": "Segmentation",
                    "target_key": "slot_groups",
                    "target_label": "Customer groups",
                    "display_order": 2,
                },
            ],
        },

        # 5 BTVTED
        {
            "category": "btvted",
            "text": "Match the learning tool to its purpose.",
            "drag_items": [
                {
                    "item_key": "vr_immersive",
                    "item_text": "VR",
                    "target_key": "slot_immersive",
                    "target_label": "Immersive simulation",
                    "display_order": 1,
                },
                {
                    "item_key": "ar_overlay",
                    "item_text": "AR",
                    "target_key": "slot_overlay",
                    "target_label": "Digital overlay",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "btvted",
            "text": "Match the gamification element to its use.",
            "drag_items": [
                {
                    "item_key": "badge_reward",
                    "item_text": "Badge",
                    "target_key": "slot_achievement",
                    "target_label": "Achievement reward",
                    "display_order": 1,
                },
                {
                    "item_key": "points_score",
                    "item_text": "Points",
                    "target_key": "slot_scorevalue",
                    "target_label": "Score value",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "btvted",
            "text": "Match the classroom technology term to its meaning.",
            "drag_items": [
                {
                    "item_key": "lms_platform",
                    "item_text": "LMS",
                    "target_key": "slot_learningplatform",
                    "target_label": "Learning platform",
                    "display_order": 1,
                },
                {
                    "item_key": "quiz_assessment",
                    "item_text": "Quiz",
                    "target_key": "slot_assessment",
                    "target_label": "Assessment tool",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "btvted",
            "text": "Match the digital literacy term to its meaning.",
            "drag_items": [
                {
                    "item_key": "source_eval",
                    "item_text": "Source Evaluation",
                    "target_key": "slot_checkcredibility",
                    "target_label": "Checks credibility",
                    "display_order": 1,
                },
                {
                    "item_key": "privacy_settings",
                    "item_text": "Privacy Settings",
                    "target_key": "slot_protectaccount",
                    "target_label": "Protects account",
                    "display_order": 2,
                },
            ],
        },
        {
            "category": "btvted",
            "text": "Match the online learning concept to its description.",
            "drag_items": [
                {
                    "item_key": "synchronous_live",
                    "item_text": "Synchronous",
                    "target_key": "slot_liveclass",
                    "target_label": "Live class",
                    "display_order": 1,
                },
                {
                    "item_key": "asynchronous_anytime",
                    "item_text": "Asynchronous",
                    "target_key": "slot_anytime",
                    "target_label": "Anytime learning",
                    "display_order": 2,
                },
            ],
        },
    ]


def seed_questions(db: Session) -> dict:
    """
    Seed target:
    - 30 multiple choice x 1 point = 30
    - 30 fill_blank_choice x 1 point = 30
    - 20 drag_drop x 2 mappings each = 40
    Perfect score = 100
    """
    mcq_data = _mcq_data()
    fill_data = _fill_blank_data()
    drag_data = _drag_drop_data()

    created_questions = 0
    created_options = 0
    created_drag_items = 0

    try:
        # MCQ
        for item in mcq_data:
            q = _get_or_create_question(
                db,
                category=item["category"],
                text=item["text"],
                question_type="mcq",
                points=1,
                time_limit_seconds=40,
            )

            for idx, (opt_text, is_correct) in enumerate(item["options"], start=1):
                _get_or_create_option(
                    db,
                    question_id=q.id,
                    text=opt_text,
                    is_correct=is_correct,
                    display_order=idx,
                )
                created_options += 1

            created_questions += 1

        # Fill in the blank button-choice
        for item in fill_data:
            q = _get_or_create_question(
                db,
                category=item["category"],
                text=item["text"],
                question_type="fill_blank_choice",
                points=1,
                time_limit_seconds=35,
                blank_placeholder=item.get("blank_placeholder", "_____"),
            )

            for idx, (opt_text, is_correct) in enumerate(item["options"], start=1):
                _get_or_create_option(
                    db,
                    question_id=q.id,
                    text=opt_text,
                    is_correct=is_correct,
                    display_order=idx,
                )
                created_options += 1

            created_questions += 1

        # Drag and drop
        for item in drag_data:
            q = _get_or_create_question(
                db,
                category=item["category"],
                text=item["text"],
                question_type="drag_drop",
                points=2,
                time_limit_seconds=75,
                image_url=item.get("image_url"),
            )

            for row in item["drag_items"]:
                _get_or_create_drag_item(
                    db,
                    question_id=q.id,
                    item_key=row["item_key"],
                    item_text=row["item_text"],
                    target_key=row["target_key"],
                    target_label=row["target_label"],
                    display_order=row.get("display_order", 0),
                )
                created_drag_items += 1

            created_questions += 1

        db.commit()
        return {
            "ok": True,
            "created_questions": created_questions,
            "mcq_questions": len(mcq_data),
            "fill_blank_questions": len(fill_data),
            "drag_drop_questions": len(drag_data),
            "created_options": created_options,
            "created_drag_items": created_drag_items,
            "perfect_score": 100,
        }

    except Exception as e:
        db.rollback()
        return {"ok": False, "error": str(e)}