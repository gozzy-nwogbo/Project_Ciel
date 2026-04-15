# Skill: Test-Driven Development

Enforces RED-GREEN-REFACTOR cycle for all feature and bugfix implementation.
Trigger: "write tests first", "TDD", "test driven", "red green refactor"
Output artifact: Passing test suite with implementation code

---

# Test-Driven Development

Enforces RED-GREEN-REFACTOR. Write tests first, always.

## When to Use

- Implementing any new feature
- Fixing any bug
- Adding any function with logic
- Any time code is about to be written

## The Cycle

### RED — Write a Failing Test
1. Write the test for the behavior you want
2. Run it and **confirm it fails** — if it passes without implementation, the test is wrong
3. The error message should make sense (not a syntax error, but a logic failure)

### GREEN — Write Minimum Code to Pass
1. Write the simplest code that makes the test pass
2. No more than necessary — resist the urge to build ahead
3. Run the test and confirm it passes

### REFACTOR — Clean Up
1. Tests still pass after refactoring? Good.
2. Remove duplication
3. Improve naming
4. Extract shared logic

Repeat the cycle for the next behavior.

## Rules

- **Never write implementation before a test** — if you catch yourself doing this, delete the code and write the test first
- **One failing test at a time** — don't write multiple failing tests before implementing
- **The test must actually fail for the right reason** — a test that passes vacuously is worse than no test
- **Commit after each GREEN** — preserve the passing state

## Anti-Patterns to Avoid

- Writing all tests upfront, then all implementation (that's not TDD, that's test-first waterfall)
- Testing implementation details instead of behavior
- Mocking everything — only mock at architectural boundaries
- Skipping the refactor step — it's not optional
- Writing tests after the fact to hit coverage metrics

## Test Structure (Arrange-Act-Assert)

```
// Arrange: set up the test state
const user = createUser({ role: 'admin' })

// Act: invoke the behavior
const result = canDeletePost(user, post)

// Assert: verify the outcome
expect(result).toBe(true)
```

## Integration with Other Skills

- `writing-plans` should create test tasks before implementation tasks
- `subagent-driven-development` subagents should follow this cycle
- `requesting-code-review` should verify TDD was followed
