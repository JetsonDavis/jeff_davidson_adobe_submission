# Research: Social Media Marketing Dashboard

**Feature**: 001-social-media-marketing  
**Date**: 2025-09-30  
**Status**: Complete

## Research Tasks

### 1. Document Processing (TXT, PDF, MS Word)

**Decision**: Use PyPDF2 for PDF, python-docx for Word, standard file reading for TXT

**Rationale**:
- PyPDF2 is lightweight, pure Python, no external dependencies
- python-docx handles .docx format natively
- Both libraries are well-maintained and widely used
- Simple text extraction is sufficient for brief content

**Alternatives Considered**:
- pdfplumber: More features but heavier dependency
- pypandoc: Requires system-level pandoc installation
- textract: Too heavyweight for simple extraction

**Implementation Notes**:
- Extract raw text from documents
- Handle encoding errors gracefully
- Display errors to user for corrupted files

### 2. LLM Integration for Idea Generation

**Decision**: Use environment-configurable LLM service (OpenAI API, local LLM, or mock for development)

**Rationale**:
- Allows flexibility in LLM choice
- Configuration via environment variables
- Easy to mock for testing and development
- User can choose based on budget/requirements

**Alternatives Considered**:
- Hard-coded OpenAI integration: Too rigid
- Multiple LLM implementations: Over-engineering for MVP
- LangChain: Too heavyweight for simple prompt/response

**Implementation Notes**:
- Use async HTTP client (httpx) for API calls
- Implement retry logic with exponential backoff
- Set 30-second timeout
- Parse region/demographic from brief content
- Return one idea per region/demographic combination

### 3. Adobe Firefly Integration

**Decision**: Use Adobe Firefly REST API with API key authentication

**Rationale**:
- Official REST API available
- Text-to-image and image compositing capabilities
- Can include text overlays and branding elements
- Supports batch generation

**Alternatives Considered**:
- DALL-E: Different provider from requirement
- Stable Diffusion: Local deployment complexity
- Midjourney: No official API

**Implementation Notes**:
- Use httpx async client
- Pass campaign message and brand colors to API
- Include region-specific language in prompts
- Store generated images in local filesystem
- Handle API rate limits and errors

### 4. File Upload Handling

**Decision**: Use FastAPI's UploadFile with python-multipart, store files locally with UUID-based naming

**Rationale**:
- FastAPI native support for file uploads
- UUID filenames prevent conflicts
- Local storage simple for development
- Easy to migrate to cloud storage later

**Alternatives Considered**:
- Direct cloud storage: Over-engineering for local dev
- Base64 encoding in database: Poor performance for images
- Original filenames: Collision risk

**Implementation Notes**:
- Validate file extensions before saving
- Limit file size to 10MB
- Create upload directories on startup
- Return file paths in API responses

### 5. Database Schema Design

**Decision**: PostgreSQL with Alembic migrations, normalized schema with foreign keys

**Rationale**:
- Constitutional requirement for PostgreSQL
- Alembic standard for FastAPI projects
- Normalized design reduces data duplication
- Foreign keys ensure referential integrity

**Key Tables**:
- briefs: Product brief content, regions, demographics, campaign message
- brand_assets: Brand logo and images, extracted colors
- product_assets: Product images
- ideas: LLM-generated ideas per region/demographic
- creatives: Firefly-generated final images
- approvals: Creative and regional approval status

**Relationships**:
- Brief 1:N Assets
- Brief 1:N Ideas
- Idea 1:N Creatives
- Creative 1:1 Approval

### 6. Frontend State Management

**Decision**: React Context API + useReducer for global state

**Rationale**:
- No external state management library needed for MVP
- React built-in solution sufficient for complexity
- Simpler than Redux/MobX for this scope
- Easy to understand and maintain

**Alternatives Considered**:
- Redux: Over-engineering for this scale
- Zustand: Unnecessary dependency
- Direct props drilling: Too many levels

**State Structure**:
- briefs: Uploaded briefs
- assets: Brand and product assets  
- ideas: Generated ideas by brief
- creatives: Final creatives in approval queue
- loading: API call status
- errors: Error messages

### 7. React Component Architecture

**Decision**: Functional components with hooks, component-per-responsibility pattern

**Components**:
- BriefUpload: Text input or file upload
- AssetUpload: Brand/product image upload with drag-drop
- AssetThumbnail: Image preview with delete button
- IdeaCard: Shows idea with regenerate/play buttons
- CreativeCard: Shows creative with approval buttons
- ApprovalQueue: Grid of creatives awaiting approval

**Styling Decision**: Use TailwindCSS for responsive design

**Rationale**:
- Utility-first CSS for rapid development
- Constitutional requirement for responsive design
- Mobile-first approach built-in
- No custom CSS needed for most components

### 8. API Design Patterns

**Decision**: RESTful API following resource-based URL structure

**Endpoints**:
- POST /briefs - Create brief (text or file)
- GET /briefs - List briefs
- DELETE /briefs/{id} - Delete brief
- POST /assets/brand - Upload brand asset
- POST /assets/product - Upload product asset
- DELETE /assets/{id} - Delete asset
- GET /assets - List assets by type
- POST /briefs/{id}/execute - Generate ideas
- POST /ideas/{id}/regenerate - Regenerate idea
- POST /ideas/{id}/generate-creative - Render with Firefly
- POST /creatives/{id}/approve-creative - Creative approval
- POST /creatives/{id}/approve-regional - Regional approval
- POST /creatives/{id}/deploy - Deploy creative
- GET /creatives - List creatives

**Rationale**:
- Standard REST conventions
- Resource-oriented URLs
- Clear action verbs for non-CRUD operations

### 9. Error Handling Strategy

**Decision**: Structured error responses with user-friendly messages

**Backend**:
- Custom exception classes for domain errors
- FastAPI exception handlers
- Structured JSON error format
- Log detailed errors server-side

**Frontend**:
- Display user-friendly error messages
- Retry prompts for recoverable errors
- Clear error states in UI
- Toast notifications for background errors

**Error Scenarios**:
- Corrupted documents: Display error, request re-upload
- LLM failure: Display error, enable re-execute
- Firefly failure: Display error, enable replay
- Network timeout: Show retry button

### 10. Performance Considerations

**File Size Limits**: 10MB per upload (configurable)

**Response Times**:
- File upload: <1 second for UI feedback
- LLM generation: <30 seconds (with progress indicator)
- Firefly rendering: <30 seconds (with progress indicator)
- Database queries: <100ms

**Concurrent Processing**:
- Async/await throughout backend
- Background task queue for long-running operations
- Frontend shows loading states during async operations

**Optimization Strategies**:
- Use async I/O for all external API calls
- Stream large file uploads
- Lazy load images in frontend
- Paginate creative queue if > 50 items

## Resolution of NEEDS CLARIFICATION

### File Size Limits
**Resolved**: 10MB per file upload (reasonable for documents and JPG images)

### Concurrent Users  
**Resolved**: Single-user local development environment (no concurrency concerns)

### Performance Targets
**Resolved**: 
- File operations: <1 second
- LLM/Firefly generation: <30 seconds with progress indicators
- Database operations: <100ms

## Technology Stack Summary

**Backend**:
- Python 3.11+
- FastAPI web framework
- SQLAlchemy ORM
- Alembic migrations
- PostgreSQL database
- PyPDF2, python-docx for documents
- httpx for async HTTP
- pytest for testing

**Frontend**:
- React 18+
- TailwindCSS for styling
- Axios for API calls
- Jest + React Testing Library
- Lucide React for icons

**Infrastructure**:
- PostgreSQL "adobe" database on port 5432
- Backend on port 8002
- Frontend on port 3001
- Local filesystem storage

## Next Steps

Proceed to Phase 1: Design & Contracts
- Extract entities for data-model.md
- Generate OpenAPI contracts
- Create contract tests
- Generate quickstart scenarios
