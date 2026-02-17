// scripts/seed-quiz.mjs
// Run: node scripts/seed-quiz.mjs
const API_BASE = (process.env.VITE_API_BASE_URL || process.env.API_BASE_URL || "").replace(/\/$/, "");
const QUIZ_PREFIX = process.env.QUIZ_PREFIX ?? "/quiz"; // set to "" if no prefix

if (!API_BASE) {
    console.error("Missing API_BASE_URL or VITE_API_BASE_URL env var");
    process.exit(1);
}

async function post(path, body) {
    const res = await fetch(`${API_BASE}${QUIZ_PREFIX}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch {}
    if (!res.ok) {
        throw new Error(`${path} failed ${res.status}: ${(data && (data.detail || data.message)) || text}`);
    }
    return data;
}

const QUIZ = [
    // --- BSCS (10)
    {
        category: "bscs",
        text: "Which approach is most used to make black-box AI models easier to understand?",
        options: [
        { text: "Model compression only", is_correct: false },
        { text: "Explainable AI (XAI) methods (e.g., SHAP/LIME)", is_correct: true },
        { text: "Increasing dataset size", is_correct: false },
        { text: "Overfitting intentionally", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "In Natural Language Processing (NLP), which model type mainly drove recent breakthroughs?",
        options: [
        { text: "Decision trees", is_correct: false },
        { text: "Transformers", is_correct: true },
        { text: "k-NN", is_correct: false },
        { text: "Naive Bayes only", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "Which algorithm is commonly used for shortest paths in weighted graphs with non-negative weights?",
        options: [
        { text: "BFS", is_correct: false },
        { text: "DFS", is_correct: false },
        { text: "Dijkstra’s Algorithm", is_correct: true },
        { text: "Kruskal’s Algorithm", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "A key ethical issue in AI systems trained on biased data is:",
        options: [
        { text: "Faster runtime", is_correct: false },
        { text: "Algorithmic unfairness/discrimination", is_correct: true },
        { text: "Perfect accuracy", is_correct: false },
        { text: "Guaranteed privacy", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "What is a typical AI technique used for fraud detection in transactions?",
        options: [
        { text: "Random guessing", is_correct: false },
        { text: "Anomaly detection using ML", is_correct: true },
        { text: "Manual inspection only", is_correct: false },
        { text: "Removing encryption", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "Autonomous vehicles primarily rely on which AI ability?",
        options: [
        { text: "File compression", is_correct: false },
        { text: "Perception + decision-making from sensor data", is_correct: true },
        { text: "Database normalization", is_correct: false },
        { text: "Text formatting", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "Which is a Divide-and-Conquer algorithm?",
        options: [
        { text: "Bubble Sort", is_correct: false },
        { text: "Merge Sort", is_correct: true },
        { text: "Linear Search", is_correct: false },
        { text: "Greedy coin change (always)", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "Which best describes a Greedy algorithm?",
        options: [
        { text: "Tries all combinations", is_correct: false },
        { text: "Chooses the locally best option each step", is_correct: true },
        { text: "Always uses recursion", is_correct: false },
        { text: "Works only on graphs", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "In predictive analytics for business, the ML output is often:",
        options: [
        { text: "A random number", is_correct: false },
        { text: "A forecast/classification to guide decisions", is_correct: true },
        { text: "Only a database schema", is_correct: false },
        { text: "A network cable configuration", is_correct: false },
        ],
    },
    {
        category: "bscs",
        text: "The biggest risk of “autonomous weapons” using AI is mainly about:",
        options: [
        { text: "Lower battery life", is_correct: false },
        { text: "Accountability and ethical responsibility for lethal decisions", is_correct: true },
        { text: "Too much storage usage", is_correct: false },
        { text: "Slow internet connection", is_correct: false },
        ],
    },

    // --- BSIT (10)
    {
        category: "bsit",
        text: "A strong ransomware defense strategy includes:",
        options: [
        { text: "Paying immediately", is_correct: false },
        { text: "Regular offline backups + patching + least privilege", is_correct: true },
        { text: "Sharing passwords", is_correct: false },
        { text: "Disabling updates forever", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "A common IoT security problem is:",
        options: [
        { text: "Too many monitors", is_correct: false },
        { text: "Weak default passwords and unpatched firmware", is_correct: true },
        { text: "Too much RAM", is_correct: false },
        { text: "Too many USB ports", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "How can AI help cybersecurity teams?",
        options: [
        { text: "By deleting all logs", is_correct: false },
        { text: "By detecting threats/anomalies faster from patterns", is_correct: true },
        { text: "By disabling encryption", is_correct: false },
        { text: "By removing access controls", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "Why is quantum computing a cybersecurity concern?",
        options: [
        { text: "It makes Wi-Fi slower", is_correct: false },
        { text: "It could break many current public-key encryption schemes", is_correct: true },
        { text: "It deletes backups", is_correct: false },
        { text: "It prevents cloud usage", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "Biometric authentication example:",
        options: [
        { text: "CAPTCHA", is_correct: false },
        { text: "Fingerprint/Face recognition", is_correct: true },
        { text: "Email address", is_correct: false },
        { text: "Device name", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "Which is a privacy-preserving technique in analytics?",
        options: [
        { text: "Posting datasets publicly", is_correct: false },
        { text: "Differential privacy", is_correct: true },
        { text: "Sharing raw identifiers", is_correct: false },
        { text: "Removing passwords only", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "Blockchain can help secure storage mainly because it is:",
        options: [
        { text: "Always free", is_correct: false },
        { text: "Tamper-evident and append-only", is_correct: true },
        { text: "Faster than RAM", is_correct: false },
        { text: "Offline by default", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "A remote work cybersecurity challenge is:",
        options: [
        { text: "Too many keyboards", is_correct: false },
        { text: "Unsecured home networks and phishing", is_correct: true },
        { text: "More monitors", is_correct: false },
        { text: "Faster CPUs", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "Social engineering prevention strategy:",
        options: [
        { text: "Ignore training", is_correct: false },
        { text: "Security awareness + verification procedures", is_correct: true },
        { text: "Share OTP codes", is_correct: false },
        { text: "Use only simple passwords", is_correct: false },
        ],
    },
    {
        category: "bsit",
        text: "A best practice in cloud security is:",
        options: [
        { text: "One password for all", is_correct: false },
        { text: "IAM least privilege + MFA + logging/monitoring", is_correct: true },
        { text: "Disable encryption", is_correct: false },
        { text: "Public admin access", is_correct: false },
        ],
    },

    // --- BSIS (10)
    {
        category: "bsis",
        text: "AI-driven personalized learning systems mainly use data to:",
        options: [
        { text: "Replace teachers completely", is_correct: false },
        { text: "Adapt content and pace per learner", is_correct: true },
        { text: "Remove assessments", is_correct: false },
        { text: "Block feedback", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "In business, predictive analytics is used to:",
        options: [
        { text: "Guess randomly", is_correct: false },
        { text: "Forecast trends (sales, churn, demand) using historical data", is_correct: true },
        { text: "Hide dashboards", is_correct: false },
        { text: "Delete customer data", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "Ethical implication of big data use includes:",
        options: [
        { text: "Less storage", is_correct: false },
        { text: "Privacy risks and potential misuse", is_correct: true },
        { text: "No need for consent", is_correct: false },
        { text: "Guaranteed fairness", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "Big data in personalized marketing often uses:",
        options: [
        { text: "Customer segmentation and recommendation models", is_correct: true },
        { text: "Manual paper surveys only", is_correct: false },
        { text: "Fax machines", is_correct: false },
        { text: "Offline-only records", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "A system that supports decision-making using visual reports is:",
        options: [
        { text: "Compiler", is_correct: false },
        { text: "Data visualization/dashboard system", is_correct: true },
        { text: "Text editor", is_correct: false },
        { text: "Antivirus only", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "Blockchain in supply chain management is useful for:",
        options: [
        { text: "Making products heavier", is_correct: false },
        { text: "Traceability and tamper-evident records", is_correct: true },
        { text: "Increasing paperwork", is_correct: false },
        { text: "Removing auditing", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "A major challenge in multi-cloud management is:",
        options: [
        { text: "Too many keyboards", is_correct: false },
        { text: "Consistent governance, security, and cost control across providers", is_correct: true },
        { text: "Lack of internet", is_correct: false },
        { text: "No user accounts", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "In e-commerce, cloud disaster recovery is important because it:",
        options: [
        { text: "Deletes data faster", is_correct: false },
        { text: "Keeps services running after failures", is_correct: true },
        { text: "Avoids customer support", is_correct: false },
        { text: "Stops scaling", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "Fake news detection on social media commonly uses:",
        options: [
        { text: "Random posts only", is_correct: false },
        { text: "NLP + classification models + network behavior signals", is_correct: true },
        { text: "Turning off comments", is_correct: false },
        { text: "Manual typing speed tests", is_correct: false },
        ],
    },
    {
        category: "bsis",
        text: "Data protection compliance in IS focuses on:",
        options: [
        { text: "Ignoring user consent", is_correct: false },
        { text: "Proper collection, storage, access control, and lawful processing", is_correct: true },
        { text: "Public passwords", is_correct: false },
        { text: "Unlimited sharing", is_correct: false },
        ],
    },

    // --- BTVTED (10)
    {
        category: "btvted",
        text: "Gamification in education aims to:",
        options: [
        { text: "Remove motivation", is_correct: false },
        { text: "Increase engagement using points, badges, challenges", is_correct: true },
        { text: "Stop feedback", is_correct: false },
        { text: "Reduce participation", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "Adaptive learning systems using AI mainly:",
        options: [
        { text: "Give the same lesson to everyone", is_correct: false },
        { text: "Adjust lessons based on learner performance data", is_correct: true },
        { text: "Remove quizzes", is_correct: false },
        { text: "Disable analytics", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "A benefit of VR in classrooms is:",
        options: [
        { text: "Less interaction", is_correct: false },
        { text: "Immersive simulations for better understanding", is_correct: true },
        { text: "No need for instruction", is_correct: false },
        { text: "Lower accessibility automatically", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "A big challenge in online learning platforms is:",
        options: [
        { text: "Too much chalk", is_correct: false },
        { text: "Maintaining student engagement and participation", is_correct: true },
        { text: "No devices exist", is_correct: false },
        { text: "No internet anywhere", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "A good digital literacy initiative should teach learners to:",
        options: [
        { text: "Share passwords", is_correct: false },
        { text: "Evaluate sources and practice online safety", is_correct: true },
        { text: "Ignore privacy settings", is_correct: false },
        { text: "Download anything", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "Ethics in educational data mining includes:",
        options: [
        { text: "Collecting data secretly", is_correct: false },
        { text: "Consent, privacy, and responsible use of learner data", is_correct: true },
        { text: "Posting grades publicly", is_correct: false },
        { text: "Removing security", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "Teacher training for tech integration should include:",
        options: [
        { text: "Only hardware repair", is_correct: false },
        { text: "Pedagogy + tools + classroom management with tech", is_correct: true },
        { text: "No lesson planning", is_correct: false },
        { text: "Avoiding assessments", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "Mobile learning apps can improve performance when they:",
        options: [
        { text: "Have no feedback", is_correct: false },
        { text: "Provide practice, feedback, and accessible content", is_correct: true },
        { text: "Only show ads", is_correct: false },
        { text: "Block offline mode always", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "AR for historical education is useful because it:",
        options: [
        { text: "Deletes history", is_correct: false },
        { text: "Adds interactive overlays (3D objects/info) to real environments", is_correct: true },
        { text: "Removes visual aids", is_correct: false },
        { text: "Makes learning text-only", is_correct: false },
        ],
    },
    {
        category: "btvted",
        text: "In HCI, accessibility means:",
        options: [
        { text: "Only design for fast internet", is_correct: false },
        { text: "Designing so people with disabilities can effectively use the system", is_correct: true },
        { text: "Using small fonts always", is_correct: false },
        { text: "Avoiding captions", is_correct: false },
        ],
    },
];

async function main() {
    console.log("Seeding quiz questions…");
    for (const q of QUIZ) {
        const createdQ = await post("/questions", { category: q.category, text: q.text });
        for (const opt of q.options) {
        await post(`/questions/${createdQ.id}/options`, opt);
        }
        console.log(`✓ ${q.category.toUpperCase()} Q${createdQ.id}`);
    }
    console.log("Done.");
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});