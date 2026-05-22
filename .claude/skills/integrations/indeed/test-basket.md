# Test Basket: indeed

## Test 1: Basic Job Search

**Input:** "Search for AI engineer jobs in Toronto"
**Expected behavior:** Call search_jobs with search: "AI engineer", location: "Toronto, ON", country_code: "CA". Return formatted results with apply links.
**Expected output:** Job listings in conversation with embedded links.

---

## Test 2: Company Data Lookup

**Input:** "What are the reviews for Anthropic on Indeed?"
**Expected behavior:** Call get_company_data with companyName: "Anthropic", knowledgeCategories: { metadata: true, ratings: true, salaries: false }.
**Expected output:** Company overview, employee ratings, culture scores.

---

## Test 3: Job Detail Retrieval

**Input:** User clicks a job ID from search results: "Get details for job abc123"
**Expected behavior:** Call get_job_details with job_id: "abc123". Return full description with apply link.
**Expected output:** Full job details with apply link intact.

---

## Test 4: Server Unreachable

**Input:** Indeed MCP returns connection error.
**Expected behavior:** Log to `00-inbox/staging/indeed-unavailable-[date].md`. Surface: "Indeed MCP is currently unreachable."
**Expected output:** No results returned, graceful error message.
