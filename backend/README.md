# Social Media Marketing Dashboard - Backend

FastAPI backend for managing product briefs, creative ideas, and social media content generation.

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 13+

### Installation

1. Create and activate virtual environment:
```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database and API keys
```

4. Run database migrations:
```bash
alembic upgrade head
```

### Running the Server

**Option 1 (Recommended):**
```bash
python run.py
```

**Option 2:**
```bash
python -m uvicorn src.main:app --reload --port 8002
```

API will be available at http://localhost:8002

## API Documentation

Once running, view interactive API docs at:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## API Endpoints

### Briefs
- `GET /briefs` - List all briefs
- `POST /briefs` - Create brief (text or file upload)
- `GET /briefs/{id}` - Get specific brief
- `DELETE /briefs/{id}` - Delete brief
- `POST /briefs/{id}/execute` - Generate ideas

### Assets
- `POST /assets/brand` - Upload brand asset
- `POST /assets/product` - Upload product asset
- `GET /assets` - List assets (with filtering)
- `DELETE /assets/{id}` - Delete asset

### Ideas
- `GET /ideas/{id}` - Get idea
- `POST /ideas/{id}/regenerate` - Regenerate idea
- `POST /ideas/{id}/generate-creative` - Generate creative

### Creatives
- `GET /creatives` - List creatives (with status filter)
- `GET /creatives/{id}` - Get creative with approval
- `POST /creatives/{id}/regenerate` - Regenerate creative

### Approvals
- `POST /creatives/{id}/approve-creative` - Approve creative
- `POST /creatives/{id}/approve-regional` - Approve regional
- `POST /creatives/{id}/deploy` - Deploy (requires both approvals)

## Testing

Run tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/contract/test_briefs_api.py
```

## Mock Mode

LLM and Adobe Firefly services automatically use mock mode when API keys are not configured. Set these in `.env` to use real services:
- `LLM_API_KEY`
- `FIREFLY_API_KEY`
