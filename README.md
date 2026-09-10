# NEXUS — Autonomous Career Intelligence Platform

> **Find roles. Understand the fit. Save the good ones. Ask Nexus. Hear what matters.**

Nexus is a full-stack career intelligence application designed to continuously scrape messy public job and internship portals, normalize raw listings using LLM structured extraction, semantically match opportunities against a candidate's uploaded resume via `pgvector`, expose the resulting data through a tool-calling AI agent, and deliver an asynchronous weekly audio/video briefing.

---

## 🏗 System Architecture

```text
┌─────────────────┐        ┌──────────────────┐        ┌────────────────────────┐
│  Next.js (Web)  │  ───>  │   FastAPI (API)  │  ───>  │  PostgreSQL + pgvector │
└─────────────────┘        └──────────────────┘        └────────────────────────┘
                                    │
                                    ▼
                               Redis Queue
                                    │
                                    ▼
                             Celery Workers
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
                 Scrapers          LLM       HeyGen / D-ID
            (httpx/bs4/Playwright) (Gemini) (ElevenLabs Fallback)
```

### Core Pipeline Flow

1. **Ingestion & Polite Scraping**: Source-adapter pattern (`BaseScraper`) with robots.txt compliance, truth in User-Agent (`NexusCareerBot/1.0`), rate-limiting with jitter, exponential backoff retries, canonical URL normalization, deterministic dedupe key uniqueness, and SHA-256 raw content hashing.
2. **Structured LLM Extraction**: Raw unstructured listing text is extracted via Google Gemini using structured schemas into a validated Pydantic model (`ExtractedListing`). Retries once with error-guided repair; caches results using `SHA256(extractor_version + model + raw_content_hash)`.
3. **Resume Parsing & Embeddings**: Resumes uploaded as PDFs are parsed with PyMuPDF, sanitized, hashed, and converted to embeddings using `SentenceTransformers` (`all-MiniLM-L6-v2`) and stored in PostgreSQL using `pgvector`.
4. **Semantic Matching & Explanations**: Cosine similarity matches listings against active resumes. High-scoring matches receive a cached 1–2 line evidence-based explanation tying resume accomplishments directly to role requirements.
5. **Autonomous Agent**: Natural language assistant using native tool calling (`search_listings`, `get_saved_listings`, `get_listings_by_deadline`, `get_skill_frequency`, `get_top_matches`). All queries strictly enforce server-side multi-tenant user scoping.
6. **Asynchronous Briefings**: Generates a 60–90 second script from the candidate's top 3 matches and submits it asynchronously to a media provider (HeyGen/D-ID with ElevenLabs audio fallback). Polling and transitions (`queued` → `processing` → `done` / `failed`) happen outside the HTTP request loop.

---

## 🎨 Design System & UI Architecture

Nexus adheres to a refined editorial aesthetic paired with modern micro-interactions:
- **Typography Pairing**:
  - **Body / Interface**: `Plus Jakarta Sans` — Crisp, geometric, high-legibility sans-serif.
  - **Display / Headings**: `Outfit` — Forward-looking, punchy display font.
- **Light & Dark Mode**:
  - **Light Canvas**: `#F7F6F2` | **Light Surface**: `#FFFFFF` | **Light Borders**: `#E7E4DF`
  - **Dark Canvas**: `#0D1114` | **Dark Surface**: `#151A1E` | **Dark Borders**: `#232C35`
  - Zero-FOUC inline script and persistent `localStorage` theme state (`nexus-theme`).
- **Official Brand Logos**:
  - Mode-responsive brand mark in top-left navigation bar with seamless light/dark mode transitions and high-resolution assets.
- **Fluid Motion (Framer Motion)**:
  - Spring-driven navigation indicators (`layoutId="navbar-active-indicator"`).
  - Staggered hero section reveals, floating interactive preview cards, and animated match badges.
  - Interactive Sun/Moon theme toggle with rotational and scale micro-interactions.
- **Shapes & Accents**:
  - Rounded cards (`rounded-card` 22px), pill badges (`rounded-pill`), buttons (`rounded-btn` 13px).
  - Restrained accents: Accent Blue (`#5278F4`), Emerald Green (`#18B978`), Amber (`#F2C94C`), Rose (`#E86A6A`).

---

## 📁 Repository Structure

```text
nexus/
├── apps/
│   ├── web/                      # Next.js 15 App Router frontend
│   │   ├── app/                  # App routes (landing, discover, shortlist, resume, agent, briefings, auth)
│   │   ├── components/           # UI primitives (Navbar, ThemeToggle)
│   │   ├── lib/                  # Utilities, API client, theme context, auth context
│   │   ├── public/               # Static assets & dark/light mode transparent logos
│   │   ├── tailwind.config.ts    # Tailwind with darkMode: "class" and CSS variable theme tokens
│   │   └── package.json
│   │
│   └── api/                      # FastAPI backend application
│       ├── app/
│       │   ├── api/v1/           # Versioned API routes (/auth, /resume, /listings, /shortlist, /agent, /briefings)
│       │   ├── core/             # Typed settings, security, logging
│       │   ├── db/               # SQLAlchemy engine, sessionmaker, Base
│       │   ├── models/           # Domain entity models (User, Listing, Match, etc.)
│       │   ├── schemas/          # Pydantic v2 schemas
│       │   ├── repositories/     # Database queries & multi-tenant isolation
│       │   ├── services/         # Business logic
│       │   ├── scraping/         # Scrapers, adapters, robots, deduplication
│       │   ├── llm/              # Gemini structured extraction & cache
│       │   ├── embeddings/       # Embedding providers & text builders
│       │   ├── agent/            # Agent orchestrator & typed database tools
│       │   ├── briefings/        # Media generators & provider adapters
│       │   └── workers/          # Celery app & background tasks
│       ├── migrations/           # Alembic database migrations
│       ├── tests/                # Pytest unit & integration tests
│       └── pyproject.toml
├── evals/                        # LLM extraction benchmark fixtures & evaluation runner
├── scripts/                      # Seed data & standalone utility scripts
├── docker-compose.yml            # Local development orchestration (Postgres+pgvector, Redis)
├── .env.example                  # Environment configuration template
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ & npm
- PostgreSQL 16+ with `pgvector` extension (or Docker)
- Redis 7+ (or Docker)

### 1. Clone & Configure Environment

```bash
cp .env.example .env
```

### 2. Backend Setup

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run tests to verify backend foundation:
```bash
python -m pytest tests/test_phase0.py -v
```

Start the API development server:
```bash
# On Linux/macOS
uvicorn app.main:app --reload --port 8000

# On Windows PowerShell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

Visit `http://localhost:3000` to view the application with automatic theme detection, dark mode toggle, and responsive logo branding.

---

## 📋 Implementation Roadmap

- [x] **Phase 0: Repository & Architecture** (Foundations, config, security, logging, test runner, monorepo layout)
- [ ] **Phase 1: Database & Authentication** (SQLAlchemy models, Alembic migrations, multi-tenant auth, user isolation)
- [ ] **Phase 2: Scraping Infrastructure** (BaseScraper, two source adapters, robots.txt, rate limits, deduplication)
- [ ] **Phase 3: LLM Extraction & Validation** (Gemini structured extraction, repair retries, extraction cache)
- [ ] **Phase 4: Resume Processing & pgvector Embeddings** (PyMuPDF parser, sentence-transformers, cosine similarity)
- [ ] **Phase 5: Matching, Semantic Search & Shortlist** (Ranked feed, evidence explanations, shortlist persistence)
- [x] **Phase 6: Frontend Core Experience** (Global shell, typography pairing, dark/light mode, Framer Motion animations, logo branding, discover, shortlist, resume, agent, briefings, auth)
- [ ] **Phase 7: Autonomous Agent & Tools** (Function-calling agent loop, scoped database tools, chat UI)
- [ ] **Phase 8: Celery & Asynchronous Briefings** (Background worker, media adapters, polling lifecycle, player)
- [ ] **Phase 9: Testing, Security & Evals** (IDOR prevention tests, extraction eval suite, prompt injection defenses)
- [ ] **Phase 10: Production Deployment & Polish** (Dockerization, Railway/Render setup, demo walkthrough)
