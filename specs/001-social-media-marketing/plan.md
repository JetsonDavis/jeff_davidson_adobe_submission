
# Implementation Plan: Social Media Marketing Dashboard

**Branch**: `001-social-media-marketing` | **Date**: 2025-09-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/jeff/Documents/PRESTON/new_spec_kit/specs/001-social-media-marketing/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Web-based social media marketing dashboard for creating multi-regional, multi-demographic campaigns. Users upload product briefs and brand/product assets, then use LLM services to generate creative ideas and Adobe Firefly to render final social media creatives. The system implements a two-stage approval workflow (creative + regional) before deployment. Backend built with Python/FastAPI, frontend with React, PostgreSQL database for persistence, and local file storage for uploaded assets.

## Technical Context
**Language/Version**: Python 3.11+ (backend), JavaScript/React 18+ (frontend)  
**Primary Dependencies**: FastAPI (backend framework), React (frontend framework), PostgreSQL (database), python-multipart (file uploads), PyPDF2/python-docx (document parsing)  
**Storage**: PostgreSQL database "adobe" on port 5432, local filesystem for uploaded assets  
**Testing**: pytest (backend), Jest + React Testing Library (frontend)  
**Target Platform**: Local development environment (macOS/Linux), Backend on port 8002, Frontend on port 3001
**Project Type**: web (frontend + backend separation)  
**Performance Goals**: Support concurrent brief processing, handle file uploads up to 10MB, LLM/Firefly generation within 30 seconds  
**Constraints**: Local-only deployment, must handle TXT/PDF/Word documents, JPG images only for assets  
**Scale/Scope**: Single-user local development, multiple concurrent campaigns, ~15-20 API endpoints

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Specification-First Development
- [x] Complete, unambiguous specification exists (spec.md)
- [x] Written for business stakeholders, not developers
- [x] NEEDS CLARIFICATION items documented (file size limits, concurrent users, performance targets - acceptable for Phase 0)

### II. Test-Driven Development
- [x] Will follow strict TDD: Tests → Fail → Implementation → Pass
- [x] Contract tests will be written for all API endpoints before implementation
- [x] Integration tests will validate all user stories

### III. Structured Workflow Gates
- [x] Following mandatory phases: Specification → Planning → Task Generation → Implementation
- [x] Quality gates established at each phase

### IV. Documentation-Driven Design
- [x] Research phase will document all design decisions with rationale
- [x] API contracts will be generated from functional requirements
- [x] Agent context file will be maintained incrementally

### V. Simplicity and Justification
- [x] Using proven patterns: REST API, standard database schema, filesystem storage
- [x] No unnecessary complexity introduced
- [x] YAGNI principles applied

### VII. Responsive Design
- [x] Frontend will be responsive (desktop, tablet, mobile)
- [x] Mobile-first approach will be used

### VIII. Infrastructure Standards
- [x] Python backend with FastAPI (constitutional requirement met)
- [x] React frontend (constitutional requirement met)
- [x] PostgreSQL for persistence (constitutional requirement met)
- [x] Standard pytest/Jest testing frameworks

**Status**: PASS - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)
```
specs/001-social-media-marketing/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   └── api-spec.yaml   # OpenAPI specification
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── src/
│   ├── models/          # SQLAlchemy models (Brief, Asset, Idea, Creative, Approval)
│   ├── schemas/         # Pydantic schemas for API validation
│   ├── services/        # Business logic (LLM, Firefly, file handling)
│   ├── api/            # FastAPI routes and endpoints
│   │   ├── briefs.py
│   │   ├── assets.py
│   │   ├── ideas.py
│   │   ├── creatives.py
│   │   └── approvals.py
│   ├── db.py           # Database connection and session management
│   └── main.py         # FastAPI app initialization
├── alembic/            # Database migrations
│   └── versions/
├── tests/
│   ├── contract/       # API contract tests
│   ├── integration/    # Integration tests
│   └── unit/          # Unit tests
├── uploads/           # Local file storage for assets
│   ├── briefs/
│   ├── brand_assets/
│   └── product_assets/
├── requirements.txt
└── alembic.ini

frontend/
├── src/
│   ├── components/     # Reusable UI components
│   │   ├── BriefUpload.jsx
│   │   ├── AssetUpload.jsx
│   │   ├── AssetThumbnail.jsx
│   │   ├── IdeaCard.jsx
│   │   ├── CreativeCard.jsx
│   │   └── ApprovalQueue.jsx
│   ├── pages/         # Main dashboard page
│   │   └── Dashboard.jsx
│   ├── services/      # API client services
│   │   └── api.js
│   ├── hooks/        # Custom React hooks
│   ├── App.jsx
│   └── index.js
├── tests/
│   ├── components/
│   └── integration/
├── package.json
└── public/
```

**Structure Decision**: Web application structure with backend/frontend separation. Backend uses FastAPI with layered architecture (models, schemas, services, API routes). Frontend uses React with component-based architecture. Database migrations managed via Alembic. Local filesystem used for uploaded asset storage in backend/uploads directory.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh windsurf`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none required)

---

## Phase Outputs Summary

### Phase 0: Research
**File**: `research.md`
- Resolved all NEEDS CLARIFICATION items (file size limits, concurrent users, performance targets)
- Researched document processing (PyPDF2, python-docx)
- Researched LLM integration patterns
- Researched Adobe Firefly API integration
- Defined database schema strategy
- Selected TailwindCSS for frontend styling
- Defined error handling approach

### Phase 1: Design & Contracts
**Files Created**:
- `data-model.md` - Complete database schema with 5 entities (Brief, Asset, Idea, Creative, Approval)
- `contracts/api-spec.yaml` - OpenAPI 3.0 specification with 15 endpoints
- `quickstart.md` - 10 integration test scenarios mapping to acceptance criteria
- `backend/tests/contract/` - Contract test files (4 files, all tests currently failing as expected):
  - `test_briefs_api.py` - 10 tests for briefs endpoints
  - `test_assets_api.py` - 8 tests for assets endpoints
  - `test_ideas_api.py` - 6 tests for ideas endpoints
  - `test_creatives_api.py` - 10 tests for creatives and approval endpoints
  - `conftest.py` - Shared test fixtures

**Contract Tests Status**: All tests currently fail (as required by TDD) - implementation needed

**API Endpoints Defined**: 15 total
- Briefs: 5 endpoints (list, create, get, delete, execute)
- Assets: 5 endpoints (upload brand, upload product, list, delete)
- Ideas: 3 endpoints (get, regenerate, generate-creative)
- Creatives: 7 endpoints (list, get, regenerate, approve-creative, approve-regional, deploy)

**Database Tables**: 5 tables with complete schema, indexes, constraints, and relationships

### Phase 3: Task Generation
**File**: `tasks.md`
- 104 numbered, ordered implementation tasks (T001-T104)
- Organized into 8 phases: Setup, Tests First, Database/Models, Services, API Endpoints, Frontend, Integration, Polish
- 34 contract tests (already created, must verify they fail)
- 5 integration test scenarios to create
- 5 frontend component test files
- TDD ordering enforced: Tests before implementation
- Parallel execution marked with [P] for 50+ independent tasks
- All tasks include exact file paths
- Dependencies clearly documented
- Estimated completion: Backend (60 tasks), Frontend (25 tasks), Integration/Polish (19 tasks)

---
*Based on Constitution v1.1.0 - See `.specify/memory/constitution.md`*
