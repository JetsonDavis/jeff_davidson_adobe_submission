# Quickstart Guide: Social Media Marketing Dashboard

**Feature**: 001-social-media-marketing  
**Date**: 2025-09-30

## Purpose

This quickstart guide provides step-by-step validation scenarios for the complete user workflow. Each scenario maps to acceptance scenarios from the feature specification and serves as integration test requirements.

## Prerequisites

**Backend**:
- PostgreSQL database "adobe" running on port 5432
- Backend server running on port 8002
- Environment variables configured (LLM API, Firefly API)
- Upload directories created

**Frontend**:
- Frontend dev server running on port 3001
- Backend API accessible

**Test Data**:
- Sample product brief (text or PDF)
- Sample brand logo (JPG)
- Sample product image (JPG)

## Scenario 1: Upload Brief and Assets

**Goal**: Validate file upload, storage, and display functionality

**Steps**:
1. Navigate to dashboard at http://localhost:3001
2. In brief upload section, either:
   - Type brief text directly into text area OR
   - Click "Upload Document" and select TXT/PDF/Word file
3. Enter campaign message: "Summer Sale - 20% Off!"
4. Enter regions (JSON): ["US", "EU", "APAC"]
5. Enter demographics (JSON): ["18-25", "25-35"]
6. Click "Create Brief"
7. In brand assets section, click "Upload Brand Asset"
8. Select JPG logo file, confirm upload
9. In product assets section, click "Upload Product Asset"
10. Select JPG product image, confirm upload

**Expected Results**:
- Brief appears in briefs list with ID
- Brief content extracted from document (if file uploaded)
- Campaign message stored correctly
- Brand asset thumbnail displayed with delete icon
- Product asset thumbnail displayed with delete icon
- Both assets show filename and file size
- Assets stored in backend/uploads/ directory

**API Calls**:
- POST /briefs (multipart/form-data)
- POST /assets/brand (multipart/form-data)
- POST /assets/product (multipart/form-data)
- GET /assets

**Validation**:
```bash
# Verify brief created
curl http://localhost:8002/briefs

# Verify assets uploaded
curl http://localhost:8002/assets

# Check filesystem
ls backend/uploads/briefs/
ls backend/uploads/brand_assets/
ls backend/uploads/product_assets/
```

## Scenario 2: Execute Brief to Generate Ideas

**Goal**: Validate LLM integration and idea generation

**Steps**:
1. Locate the brief created in Scenario 1
2. Click "Execute" button on the brief card
3. Wait for loading indicator
4. Observe ideas appearing (one per region/demographic combination)

**Expected Results**:
- Loading indicator shows "Generating ideas..."
- 6 ideas generated (3 regions × 2 demographics)
- Each idea shows:
  - Region label (US, EU, or APAC)
  - Demographic label (18-25 or 25-35)
  - Idea content text
  - Regenerate button (chasing arrows icon)
  - Play button
- Ideas persist in database

**API Calls**:
- POST /briefs/{brief_id}/execute
- GET /briefs/{brief_id} (to fetch ideas)

**Edge Case Testing**:
```bash
# Test LLM failure handling
# (Temporarily disable LLM service or use invalid API key)
# Click Execute
# Expected: Error message "LLM generation failed. Please try again."
# Re-execute button should remain active
```

**Validation**:
```bash
# Verify ideas in database
curl http://localhost:8002/briefs/{brief_id}

# Check idea count matches regions × demographics
```

## Scenario 3: Regenerate Idea

**Goal**: Validate idea regeneration without affecting other ideas

**Steps**:
1. Locate an idea card from Scenario 2
2. Note the current idea content
3. Click regenerate button (chasing arrows icon)
4. Wait for new idea to generate

**Expected Results**:
- Loading indicator on that specific idea card
- New idea content replaces old content
- Other ideas unchanged
- Generation count incremented
- Original brief and assets preserved

**API Calls**:
- POST /ideas/{idea_id}/regenerate

**Validation**:
```bash
# Verify idea updated
curl http://localhost:8002/ideas/{idea_id}

# Check generation_count incremented
# Check updated_at changed
```

## Scenario 4: Generate Creative with Adobe Firefly

**Goal**: Validate Firefly integration and creative asset generation

**Steps**:
1. Locate an idea card from Scenario 2
2. Click play button on the idea
3. Wait for loading indicator
4. Observe creative appearing in approval queue

**Expected Results**:
- Loading indicator shows "Generating creative..."
- Creative image generated and stored
- Creative appears in "Approval Queue" section
- Creative shows:
  - Generated image
  - Campaign message overlaid on image in region's language
  - Brand colors or logo incorporated
  - Region and demographic labels
  - Three buttons: Regenerate, Creative Approval, Regional Approval
  - Deploy button (disabled/inactive)
- Creative persists in database and filesystem

**API Calls**:
- POST /ideas/{idea_id}/generate-creative
- GET /creatives

**Edge Case Testing**:
```bash
# Test Firefly failure handling
# (Temporarily disable Firefly service)
# Click Play
# Expected: Error message "Firefly generation failed. Please try again."
# Play button should remain active
```

**Validation**:
```bash
# Verify creative created
curl http://localhost:8002/creatives/{creative_id}

# Check image file exists
ls backend/uploads/creatives/

# Verify approval record created with both approvals false
curl http://localhost:8002/creatives/{creative_id}
```

## Scenario 5: Grant Approvals (Creative then Regional)

**Goal**: Validate approval workflow and deploy button activation

**Steps**:
1. Locate a creative in approval queue from Scenario 4
2. Verify deploy button is inactive/disabled
3. Click "Creative Approval" button
4. Observe creative approval granted (button state changes)
5. Verify deploy button still inactive
6. Click "Regional Approval" button
7. Observe regional approval granted

**Expected Results**:
- After creative approval:
  - Creative approval button shows "Approved" state
  - Regional approval button still shows "Approve" state
  - Deploy button remains inactive
- After regional approval:
  - Both approval buttons show "Approved" state
  - Deploy button becomes active/enabled
- Approval timestamps recorded
- Creative status updated to "approved"

**API Calls**:
- POST /creatives/{creative_id}/approve-creative
- POST /creatives/{creative_id}/approve-regional
- GET /creatives (verify status)

**Validation**:
```bash
# After creative approval only
curl http://localhost:8002/creatives/{creative_id}
# Expect: creative_approved=true, regional_approved=false, deployed=false

# After both approvals
curl http://localhost:8002/creatives/{creative_id}
# Expect: creative_approved=true, regional_approved=false, deployed=false
```

## Scenario 6: Grant Approvals (Regional then Creative)

**Goal**: Validate approval order independence

**Steps**:
1. Generate another creative (repeat Scenario 4 with different idea)
2. Click "Regional Approval" button first
3. Verify deploy button still inactive
4. Click "Creative Approval" button
5. Observe deploy button becomes active

**Expected Results**:
- Regional approval granted first
- Deploy button remains inactive until creative approval also granted
- After both approvals, deploy button active
- Order doesn't matter for deploy button activation

## Scenario 7: Deploy Creative

**Goal**: Validate deployment and prevent re-deployment

**Steps**:
1. Locate a creative with both approvals from Scenario 5
2. Verify deploy button is active
3. Click "Deploy" button
4. Observe deployed banner appears

**Expected Results**:
- "Deployed" banner appears below creative image
- Deployment timestamp recorded
- Deploy button becomes inactive (cannot re-deploy)
- Creative marked as deployed in database

**API Calls**:
- POST /creatives/{creative_id}/deploy
- GET /creatives (verify deployed status)

**Edge Case Testing**:
```bash
# Try to deploy without approvals (via API)
curl -X POST http://localhost:8002/creatives/{creative_id}/deploy
# Expected: 400 Bad Request "Both approvals required"

# Try to deploy already-deployed creative
curl -X POST http://localhost:8002/creatives/{creative_id_deployed}/deploy
# Expected: 400 Bad Request "Creative already deployed"
```

**Validation**:
```bash
# Verify deployment
curl http://localhost:8002/creatives/{creative_id}
# Expect: deployed=true, deployed_at timestamp present
```

## Scenario 8: Regenerate Creative

**Goal**: Validate creative regeneration resets approval workflow

**Steps**:
1. Locate a creative (any approval state)
2. Click regenerate button on creative
3. Wait for new creative to generate
4. Observe approval buttons

**Expected Results**:
- New creative image generated
- Old image replaced with new one
- Approval status reset (both approvals false)
- Deploy button inactive again
- Generation count incremented
- User must re-approve before deploying

**API Calls**:
- POST /creatives/{creative_id}/regenerate
- GET /creatives/{creative_id}

**Validation**:
```bash
# Verify creative regenerated and approvals reset
curl http://localhost:8002/creatives/{creative_id}
# Expect: generation_count incremented, approvals reset to false
```

## Scenario 9: Delete Assets

**Goal**: Validate asset deletion and thumbnail removal

**Steps**:
1. Locate asset thumbnail (brand or product)
2. Click delete icon on thumbnail
3. Confirm deletion in prompt
4. Observe thumbnail removed

**Expected Results**:
- Thumbnail disappears from UI
- Asset removed from database
- File removed from filesystem
- Other assets unaffected

**API Calls**:
- DELETE /assets/{asset_id}
- GET /assets (verify removal)

**Validation**:
```bash
# Verify asset deleted
curl http://localhost:8002/assets
# Asset should not appear in list

# Check file removed from filesystem
ls backend/uploads/brand_assets/
ls backend/uploads/product_assets/
```

## Scenario 10: Handle Document Upload Errors

**Goal**: Validate error handling for corrupted documents

**Steps**:
1. Create corrupted PDF file (e.g., truncated file)
2. Try to upload as product brief
3. Observe error message

**Expected Results**:
- Error message displayed: "Document is corrupted or unreadable. Please re-upload."
- Brief not created
- User can retry with valid document

**API Calls**:
- POST /briefs (with corrupted file)
- Expected response: 400 Bad Request

## Performance Validation

**File Upload Performance**:
```bash
# Time file upload (should be <1 second for <10MB files)
time curl -F "file=@product_brief.pdf" -F "campaign_message=Test" \
  -F "regions=[\"US\"]" -F "demographics=[\"18-25\"]" \
  http://localhost:8002/briefs
```

**LLM Generation Performance**:
- Should complete within 30 seconds
- Progress indicator must show during generation

**Firefly Generation Performance**:
- Should complete within 30 seconds
- Progress indicator must show during generation

## Integration Test Checklist

- [ ] Scenario 1: Upload brief and assets
- [ ] Scenario 2: Execute brief to generate ideas
- [ ] Scenario 3: Regenerate idea
- [ ] Scenario 4: Generate creative with Firefly
- [ ] Scenario 5: Grant approvals (creative first)
- [ ] Scenario 6: Grant approvals (regional first)
- [ ] Scenario 7: Deploy creative
- [ ] Scenario 8: Regenerate creative
- [ ] Scenario 9: Delete assets
- [ ] Scenario 10: Handle document upload errors
- [ ] Performance validation passed
- [ ] All edge cases tested

## Success Criteria

✅ All scenarios pass without errors  
✅ Performance targets met  
✅ Error handling works as specified  
✅ Data persists correctly  
✅ UI updates reflect backend state  
✅ Workflow gates function properly (approvals before deploy)
