# Skill: Verification Before Completion

Checklist-based verification that a fix or implementation is actually complete before declaring done.
Trigger: "verify before done", "is this actually fixed", "completion check", "before merging"
Output artifact: Completed verification checklist (pass/fail per item)

---

# Verification Before Completion

Ensure it's actually fixed before saying it's done.

## When to Use

- Before marking a task complete in a plan
- Before saying "this is fixed" after debugging
- Before handing off to code review
- Before merging a branch

## Verification Checklist

### 1. The Original Issue
- [ ] Can I reproduce the original issue? (I should not be able to)
- [ ] Does the fix address the root cause, not just the symptom?
- [ ] Is there a test that would catch this regression?

### 2. Tests
- [ ] All existing tests pass
- [ ] New tests were written for the new behavior
- [ ] The new tests fail without the fix (they test the right thing)
- [ ] No tests were silently skipped or commented out

### 3. Edge Cases
- [ ] What happens with empty/null input?
- [ ] What happens at boundary values?
- [ ] What happens with concurrent access (if applicable)?
- [ ] What happens when the network/db/service is unavailable?

### 4. Regressions
- [ ] Related functionality still works
- [ ] No new warnings in the console/logs
- [ ] Performance is not significantly worse

### 5. Code Quality
- [ ] No debug logging left in (console.log, etc.)
- [ ] No commented-out code
- [ ] Variable and function names are clear
- [ ] No obvious code smell

## If Any Check Fails

Do not declare completion. Fix the issue and run the checklist again.

It is always better to take more time now than to ship a half-fix.
