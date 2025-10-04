# Epics & Delivery Timeline
## Social Media Marketing Dashboard

**Feature**: `001-social-media-marketing`  
**Created**: 2025-10-03  
**Planning Horizon**: 8 weeks  

---

## Epic Breakdown

### Epic 1: Foundation & Data Layer
**Duration**: Week 1-2 (2 weeks)  
**Priority**: P0 (Blocker)

#### Scope
Establish core data models, database schema, and API infrastructure to support the entire workflow.

#### Functional Requirements Covered
- FR-022: Persist all uploaded briefs, assets, and generated content
- FR-023: Maintain associations between briefs, assets, ideas, and creatives
- FR-024: Track approval workflow state for each creative
- FR-025: Support multiple concurrent brief processing workflows

#### Key Deliverables
- Database schema with tables: `briefs`, `assets`, `ideas`, `creatives`, `approvals`
- RESTful API endpoints for CRUD operations
- File storage system for uploaded assets
- Basic error handling and validation

#### Acceptance Criteria
- [ ] Database can store all entity types with proper relationships
- [ ] API returns appropriate status codes and error messages
- [ ] File uploads are validated and stored securely
- [ ] System supports concurrent operations without data corruption

---

### Epic 2: Content Input & Asset Management
**Duration**: Week 2-3 (2 weeks)  
**Priority**: P0 (Blocker)  
**Dependencies**: Epic 1

#### Scope
Enable users to upload product briefs and brand/product assets with visual management capabilities.

#### Functional Requirements Covered
- FR-001: Accept product briefs via text input or file upload (TXT, PDF, Word)
- FR-002: Upload areas for brand assets (JPG)
- FR-003: Upload areas for product assets (JPG)
- FR-004: Display thumbnails with delete icons
- FR-005: Delete uploaded assets via thumbnail
- FR-006: Validate file formats and reject unsupported types
- FR-007: Extract and parse content from document files

#### Key Deliverables
- Brief upload UI (text input + file upload)
- Document parser service (TXT, PDF, Word)
- Asset upload components with drag-drop support
- Thumbnail grid display with delete functionality
- File format validation (client + server)
- Error handling for corrupted/unreadable files

#### Acceptance Criteria
- [ ] Users can type or upload briefs in supported formats
- [ ] System extracts text from PDF and Word documents
- [ ] Asset thumbnails display with delete icons
- [ ] Invalid file formats are rejected with clear error messages
- [ ] Corrupted files trigger user-friendly error prompts

---

### Epic 3: LLM-Powered Idea Generation
**Duration**: Week 3-4 (2 weeks)  
**Priority**: P0 (Blocker)  
**Dependencies**: Epic 2

#### Scope
Integrate LLM service to generate creative ideas based on briefs, with regeneration capability.

#### Functional Requirements Covered
- FR-008: Execute button for each uploaded brief
- FR-009: Send brief and assets to LLM when Execute is clicked
- FR-010: Generate one idea per region/demographic combination
- FR-011: Display regenerate and play buttons for each idea
- FR-012: Regenerate button creates new idea
- FR-013: Preserve original brief and assets during regeneration

#### Key Deliverables
- LLM service integration (OpenAI/Anthropic/etc.)
- Prompt engineering for idea generation
- Execute button triggering LLM workflow
- Idea card components with region/demographic tags
- Regenerate functionality with loading states
- LLM timeout and failure handling

#### Acceptance Criteria
- [ ] Execute button generates ideas for all region/demographic combos
- [ ] Each idea displays with regenerate and play buttons
- [ ] Regeneration replaces only the specific idea
- [ ] LLM failures display error messages with retry option
- [ ] Original brief data is preserved during regeneration

---

### Epic 4: Creative Production with Adobe Firefly
**Duration**: Week 4-6 (3 weeks)  
**Priority**: P0 (Blocker)  
**Dependencies**: Epic 3

#### Scope
Generate final social media creatives using Adobe Firefly with streaming display, brand integration, and multi-language support.

#### Functional Requirements Covered
- FR-014: Play button sends brief and idea to Adobe Firefly
- FR-015: Generate final creative assets for each idea/region/demo
- FR-015a: Include campaign message in appropriate language
- FR-015b: Include brand logo or brand colors in creative
- FR-016: Place generated creatives in approval queue

#### Key Deliverables
- Adobe Firefly API integration
- Server-Sent Events (SSE) for streaming creative generation
- Progressive image display (spinners → final images)
- Brand color extraction from uploaded assets
- Logo overlay or brand color incorporation
- Multi-language text rendering (region-specific)
- Approval queue component with grid layout
- Firefly failure handling with regeneration

#### Acceptance Criteria
- [ ] Play button triggers Firefly creative generation
- [ ] Images stream in progressively (3 aspect ratios: 16:9, 9:16, 1:1)
- [ ] Campaign message appears in region's language
- [ ] Brand logo or colors are integrated into creative
- [ ] Generated creatives appear in approval queue
- [ ] Firefly failures display errors with retry option

---

### Epic 5: Approval Workflow & Deployment
**Duration**: Week 6-7 (2 weeks)  
**Priority**: P0 (Blocker)  
**Dependencies**: Epic 4

#### Scope
Implement dual-approval system (creative + regional) with deployment capability.

#### Functional Requirements Covered
- FR-017: Each creative has regenerate, creative approval, regional approval buttons
- FR-018: Track approval status independently
- FR-019: Deploy button active only when both approvals granted
- FR-020: Display "deployed" banner when deploy is clicked
- FR-021: Prevent re-deployment of deployed creatives

#### Key Deliverables
- Approval status UI (checkboxes/toggles)
- Independent tracking of creative vs. regional approval
- Deploy button with conditional activation
- Deployed banner overlay
- Deployment state persistence
- Regenerate functionality from approval queue

#### Acceptance Criteria
- [ ] Creative and regional approvals can be toggled independently
- [ ] Deploy button activates only with both approvals
- [ ] Deployed creatives show banner and disable deploy button
- [ ] Regenerated creatives reset approval state
- [ ] System prevents double-deployment

---

### Epic 6: User Experience & Polish
**Duration**: Week 7-8 (2 weeks)  
**Priority**: P1 (Important)  
**Dependencies**: Epic 5

#### Scope
Enhance UI/UX, add settings management, improve error handling, and optimize performance.

#### Key Deliverables
- Settings modal for API keys and provider selection
- Dynamic API key loading based on provider
- "Delete All" bulk action for creatives
- Loading states and progress indicators
- Responsive design for mobile/tablet
- Performance optimization (image loading, API calls)
- Comprehensive error messaging
- User guidance (tooltips, help text)

#### Acceptance Criteria
- [ ] Settings allow switching between LLM/image providers
- [ ] API keys populate automatically when provider is selected
- [ ] Bulk delete removes all creatives efficiently
- [ ] All async operations show loading indicators
- [ ] UI works on common screen sizes
- [ ] Errors provide actionable guidance

---

## Delivery Timeline

### Phase 1: Foundation (Weeks 1-2)
**Milestones:**
- Week 1: Database schema, API scaffolding, file storage setup
- Week 2: CRUD operations, validation, error handling

**Deliverable**: Working backend API with data persistence

---

### Phase 2: Content Management (Weeks 2-3)
**Milestones:**
- Week 2: Brief upload UI, document parser
- Week 3: Asset upload, thumbnail display, delete functionality

**Deliverable**: Users can upload and manage briefs and assets

---

### Phase 3: Idea Generation (Weeks 3-4)
**Milestones:**
- Week 3: LLM integration, prompt engineering
- Week 4: Execute button, idea display, regeneration

**Deliverable**: System generates LLM-powered creative ideas

---

### Phase 4: Creative Production (Weeks 4-6)
**Milestones:**
- Week 4: Firefly API integration, basic generation
- Week 5: Streaming display (SSE), brand integration
- Week 6: Multi-language support, approval queue

**Deliverable**: System produces final creatives with brand elements

---

### Phase 5: Approval & Deployment (Weeks 6-7)
**Milestones:**
- Week 6: Approval UI, status tracking
- Week 7: Deploy functionality, state management

**Deliverable**: Complete approval workflow with deployment

---

### Phase 6: Polish & Optimization (Weeks 7-8)
**Milestones:**
- Week 7: Settings UI, bulk actions, error handling
- Week 8: Performance optimization, responsive design, testing

**Deliverable**: Production-ready application

---

## Risk Mitigation

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM API failures | Medium | High | Implement retry logic, mock fallbacks, clear error messages |
| Firefly rate limits | Medium | High | Queue requests, implement backoff, show progress indicators |
| Document parsing errors | High | Medium | Support multiple parsers, validate formats, provide clear errors |
| Large file uploads | Low | Medium | Set file size limits, implement chunking, show upload progress |

### Schedule Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Firefly integration complexity | Medium | High | Allocate 3 weeks, prioritize core functionality first |
| Scope creep | Medium | High | Strict prioritization, defer P1 items if needed |
| API changes/deprecation | Low | Medium | Version pinning, monitor provider changelogs |

---

## Success Metrics

### Functional Metrics
- [ ] 100% of acceptance scenarios pass
- [ ] All P0 functional requirements implemented
- [ ] Zero data loss during uploads or generation
- [ ] Approval workflow operates without state conflicts

### Performance Metrics
- [ ] Brief upload < 2 seconds
- [ ] Asset upload < 5 seconds per file
- [ ] LLM idea generation < 30 seconds per region/demo
- [ ] Firefly creative generation < 60 seconds per aspect ratio
- [ ] Page load time < 3 seconds

### User Experience Metrics
- [ ] Error messages provide clear next steps
- [ ] All async operations show loading indicators
- [ ] UI responsive on devices ≥ 768px width
- [ ] No blocking operations > 5 seconds without progress indication

---

## Post-Launch Roadmap

### Phase 7: Analytics & Insights (Future)
- Track creative performance metrics
- A/B testing for creative variations
- Export reports for stakeholders

### Phase 8: Advanced Features (Future)
- Automated deployment to social platforms
- Scheduled posting
- Multi-campaign management
- Collaboration and commenting
