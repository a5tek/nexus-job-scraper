import html
import re
from typing import Any, Dict, List, Optional, Set


# Common UTF-8 / Windows-1252 / Latin-1 mojibake mapping
MOJIBAKE_MAP = {
    "Â·": " · ",
    "\u00c2\u00b7": " · ",
    "\u00c2": "",
    "\xe2\u2014": " - ",
    "\xe2\u2013": " - ",
    "\xe2": "",
    "\xc2": "",
    "â€“": " - ",
    "\x80\x93": " - ",
    "\xe2\x80\x93": " - ",
    "â€”": " - ",
    "\x80\x94": " - ",
    "\xe2\x80\x94": " - ",
    "\u2014": " - ",
    "\u2013": " - ",
    "â€™": "'",
    "â€˜": "'",
    "\u2018": "'",
    "\u2019": "'",
    "â€œ": '"',
    "â€\x9d": '"',
    "â€": '"',
    "\u201c": '"',
    "\u201d": '"',
    "\x80\x9c": '"',
    "\x80\x9d": '"',
    "\xa0": " ",
    "\ufffd": "",
}

# Explicit tech keywords for title verification
TECH_TITLE_KEYWORDS = [
    "software", "engineer", "developer", "programmer", "architect", "systems",
    "frontend", "front end", "front-end", "backend", "back end", "back-end",
    "fullstack", "full stack", "full-stack", "devops", "sre", "cloud",
    "infrastructure", "platform", "data scientist", "data engineer", "data analyst",
    "data science", "data analytics", "data platform", "database", "machine learning",
    "ml", "ai", "artificial intelligence", "deep learning", "nlp", "computer vision",
    "security", "cybersecurity", "appsec", "infosec", "qa", "quality assurance",
    "automation", "sdet", "test engineer", "mobile", "ios", "android",
    "firmware", "embedded", "dba", "site reliability", "network engineer",
    "web developer", "tech lead", "technical lead", "technical product",
    "product manager", "product owner", "ui/ux", "ux/ui", "ui designer",
    "ux designer", "product designer", "interaction designer", "design technologist",
    "scrum master", "solutions architect", "swe", "intern", "apprentice"
]

# Explicit non-tech exclusions that disqualify a listing unless overridden by strong tech title
NON_TECH_EXCLUSIONS = [
    "receptionist", "secretary", "paralegal", "attorney", "lawyer", "legal",
    "nurse", "nursing", "medical assistant", "dental", "physician", "therapist",
    "cashier", "barista", "waiter", "waitress", "bartender", "restaurant",
    "cider", "brewer", "dispense technician", "warehouse", "driver", "forklift",
    "construction", "carpenter", "electrician", "plumber", "cleaner", "janitor",
    "housekeep", "salon", "cosmetolog", "fitness", "trainer", "gym",
    "payroll", "bookkeeper", "accountant", "accounting assistant", "audit associate",
    "tax associate", "billing", "customer service", "customer experience",
    "customer support", "client care", "call center", "telemarket",
    "sales representative", "sales manager", "sdr", "bdr", "account executive",
    "real estate", "insurance agent", "public relations", "communications officer",
    "social comms", "social media manager", "office manager", "administrative assistant",
    "virtual assistant", "executive assistant", "people & talent", "people operations",
    "talent operations", "hr operations", "human resources", "recruiter",
    "campaign operations", "trader", "crypto analyst & trader", "dispense",
    "content writer", "course writer", "education designer", "course director",
    "care navigator", "navigator", "patient care", "health coordinator", "medical",
    "data entry", "graphic designer", "clerk", "transcription", "moderator",
]

# Tag normalization map: remoteok/raw tags -> clean standard tech skills
TAG_NORMALIZATION_MAP: Dict[str, str] = {
    "react": "React",
    "reactjs": "React",
    "react native": "React Native",
    "react-native": "React Native",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "svelte": "Svelte",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "python": "Python",
    "py": "Python",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    ".net": ".NET",
    "dotnet": ".NET",
    "java": "Java",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "ruby": "Ruby",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "php": "PHP",
    "laravel": "Laravel",
    "sql": "SQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "graphql": "GraphQL",
    "rest": "REST APIs",
    "api": "REST APIs",
    "apis": "REST APIs",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "azure": "Microsoft Azure",
    "cloud": "Cloud Computing",
    "devops": "DevOps",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "terraform": "Terraform",
    "linux": "Linux",
    "git": "Git",
    "github": "GitHub",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "css": "CSS3",
    "html": "HTML5",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "llm": "LLMs",
    "llms": "LLMs",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "kafka": "Apache Kafka",
    "spark": "Apache Spark",
    "airflow": "Apache Airflow",
    "snowflake": "Snowflake",
    "bigquery": "BigQuery",
    "figma": "Figma",
    "ui/ux": "UI/UX Design",
    "ux": "UX Design",
    "ui": "UI Design",
    "product management": "Product Management",
    "agile": "Agile",
    "scrum": "Scrum",
    "jira": "Jira",
    "microservices": "Microservices",
    "distributed systems": "Distributed Systems",
    "system design": "System Design",
    "frontend": "Frontend Development",
    "backend": "Backend Development",
    "fullstack": "Full Stack Development",
    "mobile": "Mobile Development",
    "ios": "iOS",
    "android": "Android",
    "qa": "QA Testing",
    "testing": "Software Testing",
    "cybersecurity": "Cybersecurity",
    "security": "Security",
}

# Regex patterns for accurate, false-positive-resistant text skill matching
TEXT_SKILL_PATTERNS = [
    ("Python", r"\bPython\b", False),
    ("TypeScript", r"\bTypeScript\b", False),
    ("JavaScript", r"\bJavaScript\b", False),
    ("React", r"\bReact(?:\.js)?\b", False),
    ("Next.js", r"\bNext(?:\.js)?\b", False),
    ("Vue.js", r"\bVue(?:\.js)?\b", False),
    ("Angular", r"\bAngular(?:\.js)?\b", False),
    ("Node.js", r"\bNode(?:\.js)?\b", False),
    ("Express.js", r"\bExpress(?:\.js)?\b", False),
    ("FastAPI", r"\bFastAPI\b", False),
    ("Django", r"\bDjango\b", False),
    ("Flask", r"\bFlask\b", False),
    ("Go", r"\b(?:Golang|Go)\b", True),
    ("Rust", r"\bRust\b", True),
    ("C++", r"\bC\+\+\b", False),
    ("C#", r"\bC#\b", False),
    (".NET", r"\b(?:\.NET|dotnet)\b", False),
    ("Java", r"\bJava\b(?!\s*Script)", True),
    ("Spring Boot", r"\bSpring\s*Boot\b", False),
    ("Kotlin", r"\bKotlin\b", False),
    ("Swift", r"\bSwift\b(?!\s*Taylor)", True),
    ("SQL", r"\bSQL\b", False),
    ("PostgreSQL", r"\b(?:PostgreSQL|Postgres)\b", False),
    ("MySQL", r"\bMySQL\b", False),
    ("MongoDB", r"\b(?:MongoDB|Mongo)\b", False),
    ("Redis", r"\bRedis\b", False),
    ("Elasticsearch", r"\bElasticsearch\b", False),
    ("GraphQL", r"\bGraphQL\b", False),
    ("REST APIs", r"\b(?:REST\s*APIs?|RESTful)\b", False),
    ("Docker", r"\bDocker\b", False),
    ("Kubernetes", r"\b(?:Kubernetes|K8s)\b", False),
    ("AWS", r"\bAWS\b", False),
    ("Google Cloud", r"\b(?:Google Cloud|GCP)\b", False),
    ("Microsoft Azure", r"\b(?:Azure|Microsoft Azure)\b", False),
    ("DevOps", r"\bDevOps\b", False),
    ("CI/CD", r"\bCI[/-]CD\b", False),
    ("Terraform", r"\bTerraform\b", False),
    ("Linux", r"\bLinux\b", False),
    ("Git", r"\bGit\b(?!\s*hub|\s*lab)", True),
    ("GitHub", r"\bGitHub\b", False),
    ("Tailwind CSS", r"\bTailwind(?:\s*CSS)?\b", False),
    ("HTML/CSS", r"\b(?:HTML5?|CSS3?)\b", False),
    ("Machine Learning", r"\bMachine\s+Learning\b", False),
    ("Artificial Intelligence", r"\b(?:Artificial\s+Intelligence|\bAI\b)", True),
    ("Deep Learning", r"\bDeep\s+Learning\b", False),
    ("PyTorch", r"\bPyTorch\b", False),
    ("TensorFlow", r"\bTensorFlow\b", False),
    ("Pandas", r"\bPandas\b", False),
    ("NumPy", r"\bNumPy\b", False),
    ("Apache Kafka", r"\bKafka\b", False),
    ("Apache Spark", r"\bSpark\b", False),
    ("Airflow", r"\bAirflow\b", False),
    ("Snowflake", r"\bSnowflake\b", False),
    ("Figma", r"\bFigma\b", False),
    ("UI/UX Design", r"\b(?:UI/UX|UX/UI|UI\s*Design|UX\s*Design)\b", False),
    ("Product Management", r"\bProduct\s+Management\b", False),
    ("Agile", r"\bAgile\b", False),
    ("Scrum", r"\bScrum\b", False),
    ("Microservices", r"\bMicroservices\b", False),
    ("Distributed Systems", r"\bDistributed\s+Systems\b", False),
    ("System Design", r"\bSystem\s+Design\b", False),
    ("Cybersecurity", r"\b(?:Cybersecurity|InfoSec|Application\s+Security)\b", False),
]


def sanitize_text(text: Optional[str]) -> Optional[str]:
    """
    Cleans raw strings:
    - HTML entity unescaping (&amp; -> &, &#039; -> ', &quot; -> ", etc.)
    - Mojibake correction (Â· -> ·, \x80\x93 -> –, â€” -> —, â€™ -> ')
    - Whitespace normalization
    """
    if not text:
        return None

    # 1. Unescape HTML entities
    s = html.unescape(str(text))

    # 2. Fix mojibake
    for bad, good in MOJIBAKE_MAP.items():
        if bad in s:
            s = s.replace(bad, good)

    # 3. Strip control characters while preserving newlines
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", s)
    s = s.replace("\ufffd", "–")
    s = re.sub(r"[–—]{2,}", "–", s)

    # 4. Collapse consecutive spaces/tabs
    s = re.sub(r"[ \t]+", " ", s)
    s = s.strip()
    return s if s else None


def clean_title(title: Optional[str]) -> str:
    """
    Normalizes a job title, stripping trailing location noise or junk suffixes.
    e.g. 'Product Manager · New York Chicago Charlotte' -> 'Product Manager'
         'Senior Front End Engineer Fully' -> 'Senior Front End Engineer'
         'Software Engineer - Remote' -> 'Software Engineer'
    """
    s = sanitize_text(title) or "Software Engineer"

    # Remove trailing separator suffixes like ' · New York...' or ' - Remote...'
    # If separated by middle dot, check if right side is locations
    if "·" in s:
        parts = s.split("·")
        s = parts[0].strip()

    # Remove trailing 'Fully' (often leftover from 'Fully Remote')
    s = re.sub(r"\s+Fully$", "", s, flags=re.IGNORECASE).strip()

    # Remove trailing '(US)', '(Remote)', ' - Remote'
    s = re.sub(r"\s*[-–—]\s*(?:Remote|Hybrid|Onsite|Full[\s-]?time).*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*\((?:US|USA|Remote|Hybrid|Worldwide|Global|Full[\s-]?time)\)$", "", s, flags=re.IGNORECASE)

    # Clean stray trailing punctuation
    s = s.rstrip(" -–—·,")
    return s or "Software Engineer"


def clean_company(company: Optional[str]) -> str:
    """Normalizes company name, fixing HTML entities and suffixes."""
    s = sanitize_text(company) or "Company"
    # Clean company suffixes like ', Inc.', ' LLC', etc. if messy
    s = re.sub(r"\s+(?:LLC|Inc\.|Corp\.)\s*$", "", s, flags=re.IGNORECASE).strip()
    return s or "Company"


def clean_location(location: Optional[str]) -> str:
    """
    Normalizes location strings, eliminating stuttering duplicates.
    e.g. 'California, California, United States' -> 'California, United States'
         'New York, New York, New York, United States' -> 'New York, United States'
    """
    s = sanitize_text(location)
    if not s or s.lower() in ("null", "none", "n/a", "undefined"):
        return "Remote"

    # Normalize known non-latin locations
    s_lower = s.lower()
    if any(k in s_lower for k in ("dubai", "دبي")) or "\xd8\xaf" in s:
        return "Dubai, United Arab Emirates"
    if any(k in s_lower for k in ("riyadh", "saudi", "رياض")) or "\xd8\xb1" in s or "\xd8\xb3" in s:
        return "Riyadh, Saudi Arabia"

    # Strip any remaining unprintable or non-ascii sequences
    if any(ord(ch) > 127 for ch in s):
        s = re.sub(r"[^\x20-\x7E]+", "", s).strip(" ,-")
        if not s:
            return "Remote"

    parts = [p.strip() for p in s.split(",") if p.strip()]
    seen = set()
    deduped = []
    for p in parts:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    cleaned = ", ".join(deduped)
    return cleaned if cleaned else "Remote"


def is_tech_role(
    title: str,
    tags: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> bool:
    """
    Returns True if the listing represents a technical, data, engineering,
    product, or design opportunity suitable for Nexus.
    Returns False for non-technical roles (receptionists, medical assistants,
    cider technicians, accountants, non-tech sales, customer support, etc.).
    """
    title_clean = (sanitize_text(title) or "").lower()
    if not title_clean:
        return False

    tags_clean = [t.lower().strip() for t in (tags or []) if t]

    # Strong tech tags in RemoteOK/feed
    strong_tech_tags = {
        "dev", "engineer", "engineering", "software", "tech", "technical",
        "frontend", "backend", "fullstack", "full stack", "data", "ai", "ml",
        "cloud", "devops", "sys admin", "system admin", "security", "mobile",
        "react", "python", "javascript", "typescript", "golang", "rust",
        "product", "design", "ux", "ui", "database", "analytics"
    }
    has_strong_tech_tag = any(t in strong_tech_tags for t in tags_clean)

    # 1. Disqualification check: Non-tech exclusion keywords
    is_excluded = False
    for exc in NON_TECH_EXCLUSIONS:
        if re.search(rf"\b{re.escape(exc)}\b", title_clean, re.IGNORECASE):
            is_excluded = True
            break

    # If title matched an exclusion, verify if it has an overriding tech keyword
    # e.g., 'Software Engineer in Healthcare'
    if is_excluded:
        has_tech_override = any(
            re.search(rf"\b{re.escape(k)}\b", title_clean, re.IGNORECASE)
            for k in [
                "software", "engineer", "developer", "architect",
                "machine learning", "data scientist", "data engineer"
            ]
        )
        if not has_tech_override:
            return False

    # 2. Positive qualification check on Title
    has_tech_title = any(
        re.search(rf"\b{re.escape(kw)}\b", title_clean, re.IGNORECASE)
        for kw in TECH_TITLE_KEYWORDS
    )

    if not has_tech_title:
        return False

    return True


def extract_tech_skills(
    text: str,
    tags: Optional[List[str]] = None,
    title: Optional[str] = None,
) -> List[str]:
    """
    Extracts high-quality technical skills from text, tags, and job title.
    Returns 3 to 8 relevant, deduplicated skills.
    Never falls back to arbitrary generic skills like ['Python', 'SQL'].
    """
    extracted: List[str] = []
    seen: Set[str] = set()

    def add_skill(skill: str):
        k = skill.lower()
        if k not in seen and len(extracted) < 8:
            seen.add(k)
            extracted.append(skill)

    # 1. Extract from normalized tags first (highest precision)
    for tag in tags or []:
        raw_tag = tag.strip().lower()
        # Direct match in normalization dictionary
        if raw_tag in TAG_NORMALIZATION_MAP:
            add_skill(TAG_NORMALIZATION_MAP[raw_tag])
        else:
            # Check for substring match in tag map
            for map_key, standard_skill in TAG_NORMALIZATION_MAP.items():
                if raw_tag == map_key or (len(map_key) >= 4 and map_key in raw_tag):
                    add_skill(standard_skill)
                    break

    # 2. Extract from Title (strong indicator of core stack)
    if title:
        title_lower = title.lower()
        if "frontend" in title_lower or "front end" in title_lower:
            add_skill("Frontend Development")
            add_skill("JavaScript")
            add_skill("React")
        elif "backend" in title_lower or "back end" in title_lower:
            add_skill("Backend Development")
            add_skill("REST APIs")
            add_skill("SQL")
        elif "full stack" in title_lower or "fullstack" in title_lower:
            add_skill("Full Stack Development")
            add_skill("JavaScript")
            add_skill("React")
            add_skill("Node.js")
        elif "data scientist" in title_lower:
            add_skill("Data Science")
            add_skill("Python")
            add_skill("Machine Learning")
            add_skill("SQL")
        elif "data analyst" in title_lower:
            add_skill("Data Analysis")
            add_skill("SQL")
            add_skill("Python")
        elif "data engineer" in title_lower:
            add_skill("Data Engineering")
            add_skill("Python")
            add_skill("SQL")
            add_skill("Apache Spark")
        elif "machine learning" in title_lower or "ml engineer" in title_lower:
            add_skill("Machine Learning")
            add_skill("Python")
            add_skill("PyTorch")
            add_skill("Deep Learning")
        elif "ai engineer" in title_lower:
            add_skill("Artificial Intelligence")
            add_skill("Python")
            add_skill("LLMs")
            add_skill("PyTorch")
        elif "devops" in title_lower or "sre" in title_lower:
            add_skill("DevOps")
            add_skill("CI/CD")
            add_skill("Docker")
            add_skill("Kubernetes")
            add_skill("Linux")
        elif "cloud" in title_lower:
            add_skill("Cloud Computing")
            add_skill("AWS")
            add_skill("Terraform")
        elif "security" in title_lower or "cybersecurity" in title_lower:
            add_skill("Cybersecurity")
            add_skill("Application Security")
            add_skill("Network Security")
        elif "ios" in title_lower:
            add_skill("iOS")
            add_skill("Swift")
            add_skill("Mobile Development")
        elif "android" in title_lower:
            add_skill("Android")
            add_skill("Kotlin")
            add_skill("Mobile Development")
        elif "product manager" in title_lower or "product lead" in title_lower:
            add_skill("Product Management")
            add_skill("Agile")
            add_skill("Roadmapping")
            add_skill("User Research")
        elif "ui/ux" in title_lower or "designer" in title_lower:
            add_skill("Figma")
            add_skill("UI/UX Design")
            add_skill("Wireframing")
            add_skill("User Research")
        elif "qa" in title_lower or "test" in title_lower or "sdet" in title_lower:
            add_skill("QA Testing")
            add_skill("Automation Testing")
            add_skill("CI/CD")

    # 3. Match from text patterns
    for item in TEXT_SKILL_PATTERNS:
        if len(extracted) >= 8:
            break
        skill_name = item[0]
        pattern = item[1]
        case_sensitive = item[2] if len(item) > 2 else False
        flags = 0 if case_sensitive else re.IGNORECASE
        if re.search(pattern, text, flags):
            add_skill(skill_name)

    # 4. Contextual fallback if still under 3 skills
    if len(extracted) < 3:
        if title:
            t = title.lower()
            if "intern" in t:
                add_skill("Software Engineering")
                add_skill("Git")
                add_skill("Problem Solving")
            elif "lead" in t or "manager" in t:
                add_skill("Technical Leadership")
                add_skill("System Architecture")
                add_skill("Agile")
            else:
                add_skill("Software Engineering")
                add_skill("Git")
                add_skill("System Design")
        else:
            add_skill("Software Engineering")
            add_skill("Git")

    return extracted
