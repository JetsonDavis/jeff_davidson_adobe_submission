# Windsurf Agent Context: Social Media Marketing Dashboard

## Project Overview
Web-based marketing dashboard for creating multi-regional, multi-demographic social media campaigns with AI-generated content.

## Tech Stack
**Backend**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, Alembic  
**Frontend**: React 18+, TailwindCSS, Axios  
**Testing**: pytest (backend), Jest + React Testing Library (frontend)  
**Deployment**: Local development (Backend: 8002, Frontend: 3001, PostgreSQL: 5432)

## Project Structure
```
backend/
├── src/
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic validation schemas
│   ├── services/       # Business logic (LLM, Firefly, files)
│   ├── api/           # FastAPI route handlers
│   ├── db.py          # Database connection
│   └── main.py        # App initialization
├── alembic/           # Database migrations
├── tests/
│   ├── contract/      # API contract tests
│   ├── integration/   # Integration tests
│   └── unit/         # Unit tests
└── uploads/          # Local file storage

frontend/
├── src/
│   ├── components/    # React components
│   ├── pages/        # Dashboard page
│   ├── services/     # API client
│   └── hooks/        # Custom hooks
└── tests/
```

## Database Schema
**Tables**: briefs, assets, ideas, creatives, approvals  
**Key Relationships**: Brief → Ideas → Creatives → Approval  
**Database**: PostgreSQL "adobe" on port 5432

## API Endpoints (15 total)
- POST /briefs, GET /briefs, DELETE /briefs/{id}, POST /briefs/{id}/execute
- POST /assets/brand, POST /assets/product, GET /assets, DELETE /assets/{id}
- GET /ideas/{id}, POST /ideas/{id}/regenerate, POST /ideas/{id}/generate-creative
- GET /creatives, GET /creatives/{id}, POST /creatives/{id}/regenerate
- POST /creatives/{id}/approve-creative, POST /creatives/{id}/approve-regional
- POST /creatives/{id}/deploy

## Key Features
1. Upload product briefs (text/TXT/PDF/Word) with campaign messages
2. Upload brand/product assets (JPG only, max 10MB)
3. Execute briefs to generate LLM-powered creative ideas per region/demographic
4. Generate final creatives with Adobe Firefly (includes campaign message + branding)
5. Two-stage approval workflow (creative + regional)
6. Deploy only when both approvals granted

## Development Workflow
Following Spec Kit Constitution v1.1.0:
- Specification-first development
- Strict TDD (tests before implementation)
- Contract tests already created (currently failing)
- All design artifacts in specs/001-social-media-marketing/

## Current Status
- Phase 0-2 complete (Research, Design, Planning)
- Ready for Phase 3: /tasks command to generate implementation tasks
- Contract tests exist but fail (awaiting implementation)

## External Dependencies
- LLM API (configurable via environment)
- Adobe Firefly API (for creative generation)
- Document parsing: PyPDF2, python-docx

## Recent Changes
- 2025-09-30: Initial planning complete, contract tests created
