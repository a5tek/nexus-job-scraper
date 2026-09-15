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

### 4. Security & Authentication Architecture
- **HttpOnly Cookie Authentication**: Session tokens are automatically issued as `HttpOnly`, `SameSite=Lax`, `Secure` (production) cookies, mitigating client-side XSS token theft vectors. Bearer tokens remain supported for backward-compatible headless clients.
- **Endpoint Rate Limiting**: SlowAPI protection on `/auth/login` (10/min) and `/auth/register` (5/min) to prevent brute-force credential stuffing.
- **Fail-Closed Secret Validation**: Startup lifespan validates that production environments cannot boot with default or short secret keys.
- **Multi-Stage Container Security**: `apps/api/Dockerfile` runs as an unprivileged user (`appuser:appgroup`) with integrated health checks.

### 5. Multi-Source Scraping Pipeline
- **RemoteOK Public JSON API (`remoteok`)**: Live remote developer roles ingested directly via structured JSON with compensation, tags, and direct apply links.
- **SimplifyJobs GitHub Aggregator (`github_internships`)**: 1,750+ verified tech internship opportunities parsed from structured community markdown/HTML tables with automated closed-posting filtering (`🔒`).
- **YC Work at a Startup (`yc_jobs`)**: Structured card parser with dynamic headless Chromium support (`PlaywrightScraperClient`) and graceful fallback.
- **Connection-Pooled Client**: `PoliteScraperClient` with persistent connection pooling (20 max connections, 10 keepalive), per-domain rate limiting with jitter, and robots.txt caching.

### 6. Frontend Architecture & Responsiveness
- **Mobile Navigation Drawer**: Responsive hamburger button (`md:hidden`) with animated slide-out menu drawer powered by Framer Motion `AnimatePresence`, full-screen backdrop, keyboard (`Escape`) and route-change dismiss.
- **Component Decomposition**: Clean separation of concerns with modular sub-components: `ListingCard` (opportunity badges, match score, deadline countdown, expandable match justification), `FilterBar` (search with live loading and filter toggles), `UploadDropzone` (drag-and-drop validation, size limits), and `ResumeStatus` (stepper progress tracker, recalculate action, parsed text drawer).
- **Single Theme-Aware Logo Loading**: Replaced redundant dual-image DOM loading with `components/Logo.tsx` consuming `resolvedTheme` to render a single optimized `<Image priority />`, eliminating wasted bandwidth.
- **Centralized Types & Strict Typing**: Centralized all TypeScript definitions in `types/index.ts`. Completely eliminated `err: any` and all `: any` occurrences across the entire web application, adopting safe `err: unknown` type narrowing.
- **Robust API Client**: `apiClient` transparently handles `FormData` file uploads (omits `Content-Type` for browser multipart boundary generation) and JSON payloads with credentials cookie forwarding.

### 7. Infrastructure, Quality & Continuous Integration
- **GitHub Actions CI/CD Pipeline (`.github/workflows/ci.yml`)**: Fully automated matrix running Ruff code linting, Bandit static security scans, PostgreSQL 16 (pgvector) and Redis service containers with pytest coverage, Vitest frontend component tests, Next.js build verification, and multi-stage Docker build checks.
- **Frontend Unit Testing**: Installed and configured Vitest + JSDOM + `@testing-library/react` suite. Fast, isolated component tests covering search filtering, opportunity cards, upload dropzone validations, and logo theme reactivity.
- **Database Connection Pooling & Vector Optimization**: Configured production asyncpg connection pool parameters (`pool_size=10`, `max_overflow=5`, `pool_timeout=30`, `pool_recycle=1800`, `pool_pre_ping=True`) and applied Alembic migration creating HNSW indexes (`vector_cosine_ops`) on `listings.embedding` and `resumes.embedding`.
- **Dependency & Supply Chain**: Added `asyncpg`, `aiosqlite`, `sentence-transformers`, and `sentry-sdk[fastapi]` to eliminate runtime driver gaps.

---

## 📋 Implementation Roadmap

- [x] **Phase 0: Repository & Architecture** (Foundations, config, security, logging, test runner, monorepo layout)
- [x] **Phase 1: Security & Authentication Hardening** (HttpOnly cookies, SlowAPI rate limiting, container privilege drop, credential isolation)
- [x] **Phase 2: Scraping Infrastructure & Real Sources** (BaseScraper, RemoteOK API, SimplifyJobs GitHub tables, connection pooling, Playwright integration)
- [x] **Phase 3: Frontend Quality & Responsiveness** (Mobile drawer, error feedback, component decomposition, theme image optimization, centralized types)
- [x] **Phase 4: Infrastructure, CI/CD & Testing** (GitHub Actions CI/CD, Vitest suite, pgvector HNSW index, connection pooling, asyncpg)
- [ ] **Phase 5: Polish & Production Readiness** (Password policy validator, strict CORS, refresh token rotation, observability)
- [x] **Phase 7: Frontend Core Experience** (Global shell, typography pairing, dark/light mode, Framer Motion animations, logo branding)
- [ ] **Phase 8: Autonomous Agent & Tools** (Function-calling agent loop, scoped database tools, chat UI)
- [ ] **Phase 9: Celery & Asynchronous Briefings** (Background worker, media adapters, polling lifecycle, player)
- [ ] **Phase 10: Production Deployment & CI/CD** (GitHub Actions CI, Docker builds, health checks, demo walkthrough)
