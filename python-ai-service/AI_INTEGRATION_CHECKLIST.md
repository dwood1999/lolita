# AI API Integration Completion Checklist

## CRITICAL: Complete ALL steps below for every new AI feature/API integration

### 1. API Implementation (Backend)
- [ ] Create or update analyzer class with new functionality
- [ ] Add proper error handling and logging
- [ ] Include cost tracking and timing
- [ ] Add result dataclass/model
- [ ] Test API calls work correctly

### 2. Database Integration
- [ ] Add new fields to database schema (SQL migration files)
- [ ] Update database.py with new fields
- [ ] Add to_database_format() method in analyzer
- [ ] Test database saves work correctly

### 3. Main Service Integration
- [ ] Import new analyzer in main.py
- [ ] Initialize analyzer in startup
- [ ] Add to parallel processing tasks
- [ ] Handle results in analysis workflow
- [ ] Update progress tracking messages
- [ ] Save results to database

### 4. API Endpoints (Backend)
- [ ] Update analysis result endpoints to include new data
- [ ] Add specific endpoints if needed (e.g., /api/analysis/{id}/ip-assessment)
- [ ] Test endpoints return correct data
- [ ] Update API response models

### 5. Frontend Integration
- [ ] Update TypeScript types for new data
- [ ] Add UI components to display results
- [ ] Update analysis results page
- [ ] Add loading states and error handling
- [ ] Style components appropriately
- [ ] Test frontend displays data correctly

### 6. File Management (if applicable)
- [ ] Create proper directory structure
- [ ] Implement file saving with proper naming
- [ ] Add file serving endpoints
- [ ] Update static file handling
- [ ] Test file access works

### 7. Testing & Validation
- [ ] Test complete end-to-end flow
- [ ] Verify data persists correctly
- [ ] Check error handling works
- [ ] Validate cost tracking
- [ ] Test with different input types

## Example: IP Assessment Integration

### Backend Implementation:
```python
# 1. Add to analyzer (e.g., claude_analyzer.py)
async def assess_ip_potential(self, screenplay_text: str, title: str) -> IPAssessmentResult:
    # Implementation here
    pass

# 2. Add result dataclass
@dataclass
class IPAssessmentResult:
    franchise_potential: float
    merchandising_score: float
    sequel_viability: str
    adaptation_opportunities: List[str]
    market_comparisons: List[str]
    # etc.
```

### Database Updates:
```sql
-- Add to migration file
ALTER TABLE analyses ADD COLUMN ip_franchise_potential DECIMAL(3,2);
ALTER TABLE analyses ADD COLUMN ip_merchandising_score DECIMAL(3,2);
ALTER TABLE analyses ADD COLUMN ip_sequel_viability TEXT;
-- etc.
```

### Main Service Integration:
```python
# In process_analysis functions
ip_result = await claude_analyzer.assess_ip_potential(screenplay_text, title)
# Save to database
# Add to progress updates
```

### Frontend Integration:
```typescript
// Update types
interface AnalysisResult {
  // existing fields...
  ip_assessment?: {
    franchise_potential: number;
    merchandising_score: number;
    sequel_viability: string;
    // etc.
  }
}
```

```svelte
<!-- Add to analysis results page -->
{#if analysis.ip_assessment}
  <div class="ip-assessment-section">
    <h3>IP Potential Assessment</h3>
    <div class="franchise-score">
      Franchise Potential: {analysis.ip_assessment.franchise_potential}/10
    </div>
    <!-- More UI components -->
  </div>
{/if}
```

## Common Mistakes to Avoid:
1. ❌ Implementing API call but not saving to database
2. ❌ Saving to database but not updating frontend
3. ❌ Adding frontend display but not updating API endpoints
4. ❌ Forgetting to add to parallel processing tasks
5. ❌ Not updating progress tracking messages
6. ❌ Missing error handling in any layer
7. ❌ Not testing the complete end-to-end flow

## Verification Steps:
1. ✅ Can I see the new data in database after analysis?
2. ✅ Does the API endpoint return the new data?
3. ✅ Does the frontend display the new information?
4. ✅ Do error cases handle gracefully?
5. ✅ Are costs tracked properly?
6. ✅ Does the feature work for both text and PDF uploads?

## Template Commit Messages:
- "Add [feature] API integration with complete backend/frontend flow"
- "Implement [feature] assessment with database persistence and UI display"
- "Complete [feature] integration: API → Database → Frontend"

---

**REMEMBER: No integration is complete until the user can see the results in the frontend!**
