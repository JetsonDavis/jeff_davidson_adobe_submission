# Social Media Marketing Dashboard

AI-powered social media marketing dashboard for multi-regional, multi-demographic campaigns.

## Features

- Upload product briefs (text or documents: TXT, PDF, Word)
- Upload brand and product assets (JPG images)
- Generate creative ideas using LLM (one per region/demographic)
- Generate social media creatives with Adobe Firefly
- Two-stage approval workflow (creative + regional)
- Deploy approved content

## Project Structure

```
backend/          # FastAPI backend (Python 3.11+)
frontend/         # React frontend (Vite + TailwindCSS)
specs/            # Feature specifications and design docs
```

## Quick Start

### System Pre-Requistes

- Python 3.11+
- PostgreSQL 15+
- Node.js 20+
- npm 9+
- Git
- Homebrew

Make sure you have all of the above installed on your system.

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with DATABASE_URL and API keys

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload --port 8002
```

Backend runs at http://localhost:8002

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at http://localhost:3001

### Database Setup

Create PostgreSQL database:
```bash
createdb adobe
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Run Specific Tests
```bash
pytest tests/contract/test_briefs_api.py
pytest tests/integration/
```

## Architecture

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React 19 + TailwindCSS + Vite
- **APIs**: LLM for ideas, Adobe Firefly for creatives
- **Storage**: PostgreSQL DB + local filesystem for assets

## Development

Built following TDD principles with comprehensive test coverage:
- 34 contract tests for API endpoints
- 5 integration test scenarios
- All tests written before implementation

## Documentation

- API Docs: http://localhost:8002/docs (Swagger UI)
- Feature Spec: `specs/001-social-media-marketing/spec.md`
- Implementation Plan: `specs/001-social-media-marketing/plan.md`
- Tasks: `specs/001-social-media-marketing/tasks.md`

## Mock Mode

LLM and Firefly services run in mock mode by default.  To add real API keys, run the web site and click the gear icon in the upper right of the screen.  Here, you can add your API keys for your LLM and image generation services.

