# DOCMIND

[![CI](https://github.com/YOUR_USERNAME/docmind/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/docmind/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-grade RAG (Retrieval-Augmented Generation) pipeline that lets you upload PDFs and ask questions about their content using natural language.

Built with FastAPI, PostgreSQL + pgvector, OpenAI, and LangChain.

---

## Architecture

```text
UPLOAD FLOW

  POST /documents/upload
        |
        v
  +------------+   +--------------+   +-------------+   +-----------+
  | PDF Parser |-->|    Chunker   |-->| Embeddings  |-->| pgvector  |
  | (PyMuPDF)  |   | (Recursive)  |   |  (OpenAI)   |   |   Store   |
  +------------+   +--------------+   +-------------+   +-----------+

QUERY FLOW

  POST /qa/ask
        |
        v
  +------------+   +--------------+   +-------------+   +-----------+
  | PII Redact |-->| Embed        |-->| Top-K       |-->| LLM (GPT) |
  | + Validate |   | Question     |   | Retrieval   |   | Generation|
  +------------+   +--------------+   +-------------+   +-----------+
                                                              |
                                                              v
                                                         Answer + Refs
```

**Upload Flow:** PDF -> Extract text (PyMuPDF) -> Split into chunks (LangChain) -> Generate embeddings (OpenAI) -> Store in PostgreSQL (pgvector)
**Query Flow:** Question -> PII redaction -> Generate embedding -> Vector similarity search -> Pass top-K chunks to LLM -> Return answer with source references

## Features

| Feature              | Description                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| **RAG Pipeline**     | End-to-end PDF upload -> chunking -> embedding -> retrieval -> LLM answer |
| **Vector Search**    | pgvector cosine similarity with configurable top-K                        |
| **PII Redaction**    | Emails, phones, SSNs, credit cards scrubbed before LLM calls              |
| **API Key Auth**     | `X-API-Key` header auth, configurable per environment                     |
| **Rate Limiting**    | Per-IP rate limits on LLM endpoints (10/min on `/qa/ask`)                 |
| **Retry Logic**      | Exponential backoff on transient OpenAI failures                          |
| **Pagination**       | Offset/limit pagination with `has_more` on list endpoints                 |
| **Error Handling**   | Custom exception hierarchy with double-fault-safe global handler          |
| **Request Logging**  | Structured JSON logs with correlation IDs, method, path, duration         |
| **Input Validation** | MIME type + 50 MB file size checks on uploads                             |
| **CI/CD**            | GitHub Actions: lint (ruff) + test (pytest with pgvector)                 |
| **Docker**           | Multi-stage build, non-root user, healthcheck                             |

## Tech Stack

| Component      | Technology                               | Why                                         |
| -------------- | ---------------------------------------- | ------------------------------------------- |
| API Framework  | FastAPI                                  | Async, auto-docs, type-safe                 |
| PDF Parsing    | PyMuPDF (fitz)                           | Fast, handles complex PDFs                  |
| Text Splitting | LangChain RecursiveCharacterTextSplitter | Respects document structure                 |
| Embeddings     | OpenAI text-embedding-3-small            | Good quality, cost-effective                |
| Vector Store   | PostgreSQL + pgvector                    | Production-ready, no extra infra            |
| LLM            | OpenAI GPT-4o-mini                       | Fast, cheap, good for QA                    |
| ORM            | SQLAlchemy 2.0 (async)                   | Async support, mature ecosystem             |
| Migrations     | Alembic                                  | Version-controlled schema changes           |
| Auth           | API Key (X-API-Key header)               | Lightweight, configurable per env           |
| Rate Limiting  | slowapi                                  | Per-IP limits on expensive endpoints        |
| Logging        | structlog (JSON)                         | Structured, machine-parseable               |
| Linting        | Ruff                                     | Fast, replaces flake8 + isort + black       |
| CI             | GitHub Actions                           | Lint + test with pgvector service container |

## API Endpoints

| Method   | Endpoint                   | Auth | Description                           |
| -------- | -------------------------- | ---- | ------------------------------------- |
| `POST`   | `/api/v1/documents/upload` | Yes  | Upload a PDF and process it           |
| `GET`    | `/api/v1/documents`        | Yes  | List documents (paginated)            |
| `GET`    | `/api/v1/documents/{id}`   | Yes  | Get document details                  |
| `DELETE` | `/api/v1/documents/{id}`   | Yes  | Delete document and chunks            |
| `POST`   | `/api/v1/qa/ask`           | Yes  | Ask a question (rate limited: 10/min) |
| `GET`    | `/api/v1/health`           | No   | Health check (always public)          |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Run

```bash
# 1. Clone
git clone [https://github.com/YOUR_USERNAME/docmind.git](https://github.com/YOUR_USERNAME/docmind.git)
cd docmind

# 2. Configure
cp .env.example .env
# Edit .env - add your OPENAI_API_KEY

# 3. Start
make up
# Or: docker-compose up --build

# 4. Run migrations
make migrate

# 5. Open docs
open http://localhost:8000/docs
```

### Try It

```bash
# Upload a PDF
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@sample_docs/sample.pdf"

# List documents (paginated)
curl "http://localhost:8000/api/v1/documents?offset=0&limit=10"

# Ask a question
curl -X POST http://localhost:8000/api/v1/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key points?", "top_k": 5}'

# Health check
curl http://localhost:8000/api/v1/health
```

### Local Development

```bash
# Install dependencies with uv
uv pip install -e ".[dev]" --python .venv/bin/python

# Start DB only
docker-compose up db -d

# Run app with hot reload
make run

# Format + lint
make format
make lint

# Run tests
make test

# Coverage report
make coverage
```

## Project Structure

```text
docmind/
├── app/
│   ├── main.py                 # FastAPI app, middleware, lifespan
│   ├── api/v1/
│   │   ├── routes/
│   │   │   ├── documents.py    # Upload, list, get, delete (paginated)
│   │   │   ├── qa.py           # Question answering (rate limited)
│   │   │   └── health.py       # Health check
│   │   └── dependencies.py     # Service factory functions
│   ├── core/
│   │   ├── config.py           # Pydantic Settings (env vars)
│   │   ├── exceptions.py       # APIError hierarchy
│   │   ├── logging.py          # structlog setup
│   │   ├── openai_client.py    # Shared singleton + retry decorator
│   │   ├── pii.py              # PII redaction (email, phone, SSN, CC)
│   │   └── prompts.py          # LLM prompt templates
│   ├── db/
│   │   ├── base.py             # SQLAlchemy declarative base
│   │   └── session.py          # Async engine + session factory
│   ├── middleware/
│   │   ├── auth.py             # API key authentication
│   │   ├── correlation.py      # Correlation ID + request logging
│   │   ├── error_handler.py    # Global error handlers (double-fault-safe)
│   │   └── rate_limit.py       # slowapi rate limiter
│   ├── models/
│   │   ├── domain.py           # Document + Chunk (pgvector)
│   │   └── schemas.py          # Request/response models + pagination
│   └── services/
│       ├── pdf_parser.py       # PDF text extraction (PyMuPDF)
│       ├── chunker.py          # Recursive text splitting
│       ├── embeddings.py       # OpenAI embedding generation
│       ├── vector_store.py     # pgvector CRUD + similarity search
│       └── qa_chain.py         # RAG pipeline orchestration
├── alembic/
│   ├── env.py                  # Async migration runner
│   └── versions/
│       └── 001_initial_schema.py # Documents + chunks tables
├── tests/
│   ├── conftest.py             # Test fixtures (PDF generation)
│   ├── test_api.py             # API route tests
│   ├── test_auth.py            # Auth middleware tests
│   ├── test_chunker.py         # Chunking logic tests
│   ├── test_openai_client.py   # Retry decorator tests
│   ├── test_pdf_parser.py      # PDF parsing tests
│   └── test_pii.py             # PII redaction tests
├── .github/workflows/ci.yml    # Lint + test pipeline
├── docker-compose.yml          # Production-like setup
├── docker-compose.dev.yml      # Dev override (volume mount + reload)
├── Dockerfile                  # Multi-stage build, non-root user
├── Makefile                    # Dev commands (format, lint, test, run, up)
├── pyproject.toml              # Dependencies + tool config
├── alembic.ini                 # Migration config
├── .env.example                # Environment variable template
├── CLAUDE.md                   # AI assistant context
└── LICENSE                     # MIT
```

## Configuration

All settings via environment variables. See `.env.example` for the full list.

| Variable          | Description                              | Default                                                |
| ----------------- | ---------------------------------------- | ------------------------------------------------------ |
| `OPENAI_API_KEY`  | OpenAI API key                           | **required**                                           |
| `DATABASE_URL`    | PostgreSQL connection string             | `postgresql+asyncpg://postgres:postgres@db:5432/ragdb` |
| `EMBEDDING_MODEL` | Embedding model                          | `text-embedding-3-small`                               |
| `LLM_MODEL`       | Chat model                               | `gpt-4o-mini`                                          |
| `CHUNK_SIZE`      | Characters per chunk                     | `1000`                                                 |
| `CHUNK_OVERLAP`   | Overlap between chunks                   | `200`                                                  |
| `TOP_K`           | Default chunks to retrieve               | `5`                                                    |
| `REQUIRE_AUTH`    | Enable API key auth                      | `false`                                                |
| `API_KEY`         | API key value (when auth enabled)        | `""`                                                   |
| `CORS_ORIGINS`    | Allowed CORS origins                     | `["http://localhost:3000","http://localhost:5173"]`    |
| `APP_ENV`         | Environment (`development`/`production`) | `development`                                          |
| `LOG_LEVEL`       | Log level                                | `INFO`                                                 |

## Key Design Decisions

1. **pgvector over Pinecone/Weaviate** - No external dependency. PostgreSQL handles both relational data and vectors. One database to deploy and operate.
2. **Recursive chunking over fixed-size** - Respects paragraph and sentence boundaries. Produces more meaningful chunks for retrieval.
3. **async everywhere** - `asyncpg` + async SQLAlchemy + async FastAPI. No blocking the event loop on I/O.
4. **PII redaction before LLM calls** - Regex-based scrubbing of emails, phones, SSNs, credit cards. Documents may contain sensitive data that shouldn't reach external APIs.
5. **shared OpenAI client with retries** - Singleton `AsyncOpenAI` with exponential-backoff retry on transient errors (connection, timeout, rate limit). No duplicate clients.
6. **fail-open auth in dev, fail-closed in prod** - `REQUIRE_AUTH=false` locally so you don't need a key for development. `REQUIRE_AUTH=true` in production with a real `API_KEY`.
7. **Separation of concerns** - Services are independent. Swap PyMuPDF for another parser, or pgvector for another vector store, without touching the API layer.
8. **alembic over create_all()** - Version-controlled migrations. Safe for production deployments where tables already exist.

## License

MIT ([LICENSE](LICENSE))
