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

## 🎨 Design System (DESIGN.md Reference)

Nexus adheres to an editorial, warm, approachable visual identity:
- **Canvas**: Warm off-white (`#F7F6F2`)
- **Surface**: Pure warm white (`#FFFFFF`)
- **Primary Text**: Near-black brown (`#302A29`)
- **Secondary Text**: Muted warm gray (`#77736F`)
- **Borders**: Subtle warm gray (`#E7E4DF`)
- **Accent Blue**: Restrained vivid blue (`#5278F4`)
- **Success Green**: Fresh emerald green (`#18B978`)
- **Shapes**: Rounded cards (22px radius), pill badges, comfortable buttons (13px radius)
- **Hierarchy**: High whitespace, low visual noise, progressive disclosure.

---

## 📁 Repository Structure

```text
nexus/
├── apps/
│   ├── web/                      # Next.js 15 App Router frontend
│   │   ├── app/                  # App routes (landing, discover, shortlist, etc.)
│   │   ├── components/           # Reusable UI primitives & layout shells
│   │   ├── lib/                  # Utilities, API client, design tokens
│   │   └── package.json
│   │
│   └── api/                      # FastAPI backend application
│       ├── app/
│       │   ├── api/v1/           # Versioned API routes (/auth, /resume, /listings, etc.)
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
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

Visit `http://localhost:3000` to view the application.

---

## 📋 Implementation Roadmap

- [x] **Phase 0: Repository & Architecture** (Foundations, config, security, logging, test runner, monorepo layout)
- [ ] **Phase 1: Database & Authentication** (SQLAlchemy models, Alembic migrations, multi-tenant auth, user isolation)
- [ ] **Phase 2: Scraping Infrastructure** (BaseScraper, two source adapters, robots.txt, rate limits, deduplication)
- [ ] **Phase 3: LLM Extraction & Validation** (Gemini structured extraction, repair retries, extraction cache)
- [ ] **Phase 4: Resume Processing & pgvector Embeddings** (PyMuPDF parser, sentence-transformers, cosine similarity)
- [ ] **Phase 5: Matching, Semantic Search & Shortlist** (Ranked feed, evidence explanations, shortlist persistence)
- [ ] **Phase 6: Frontend Core Experience** (Global shell, sidebar, discover, filters, cards, detail modal)
- [ ] **Phase 7: Autonomous Agent & Tools** (Function-calling agent loop, scoped database tools, chat UI)
- [ ] **Phase 8: Celery & Asynchronous Briefings** (Background worker, media adapters, polling lifecycle, player)
- [ ] **Phase 9: Testing, Security & Evals** (IDOR prevention tests, extraction eval suite, prompt injection defenses)
- [ ] **Phase 10: Production Deployment & Polish** (Dockerization, Railway/Render setup, demo walkthrough)
