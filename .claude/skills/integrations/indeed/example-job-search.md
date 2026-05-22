# Worked Example: Indeed Job Search

## Input
User: "Search for AI engineer jobs in Toronto on Indeed"

## Process
1. Call `search_jobs` with search: "AI engineer", location: "Toronto, ON", country_code: "CA"
2. Receive list of job results
3. Cross-reference against user.md for fit scoring
4. Surface results with apply links embedded in titles
5. Log high-fit leads to Supabase captures table

## Output (in conversation)
```
Found 10 AI engineer jobs in Toronto:

1. [Senior AI Engineer at Anthropic](apply-link) — **High fit** (agent architecture, Claude experience)
   $150K-200K | Full-time | Toronto, ON

2. [ML Engineer at Shopify](apply-link) — **Medium fit** (ML focus, less agent work)
   $130K-170K | Full-time | Toronto, ON

...
```

## Event Log Entry
```json
{
  "timestamp": "2026-04-16T15:30:00Z",
  "session_id": "session-123",
  "action": "indeed_search",
  "integration": "indeed",
  "permission_tier": "read-only",
  "inputs_summary": "search: AI engineer, location: Toronto ON, country: CA",
  "result": "success",
  "reason": "User requested job search for AI engineer roles in Toronto"
}
```
