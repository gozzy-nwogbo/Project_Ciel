# Skill: Systematic Debugging

4-phase root cause analysis: Observe, Hypothesize, Experiment, Fix.
Trigger: "debug this", "why is this failing", "root cause", "systematic debugging"
Output artifact: Root cause diagnosis with regression test

---

# Systematic Debugging

4-phase root cause process. Systematic over ad-hoc — process over guessing.

## When to Use

- A bug is unclear or hard to reproduce
- Previous fix attempts haven't worked
- An error trace points deep into library code
- "It works on my machine" situations

## The 4 Phases

### Phase 1: Observe
Gather all available evidence before forming any hypothesis.

- What is the exact error message?
- What is the full stack trace?
- When does it happen? (always / sometimes / specific input)
- When did it start? (recent change / always existed)
- What environment? (OS, version, config)

Do not touch code in this phase.

### Phase 2: Hypothesize
Form one specific hypothesis about the root cause.

- A hypothesis is: "I believe X is happening because Y"
- Not: "Maybe it's the database" — too vague
- Yes: "I believe the null check on line 42 is missing when `user` is unauthenticated"

Write the hypothesis down before testing it.

### Phase 3: Experiment
Test the hypothesis with the minimal possible change.

- Add logging/assertions to confirm or deny the hypothesis
- Do not fix yet — just confirm what's actually happening
- Use `console.log`, breakpoints, or test cases to gather evidence
- If the hypothesis is wrong, return to Phase 2 with new information

### Phase 4: Fix
Only now write the fix, and only for the confirmed root cause.

- The fix should be small and targeted
- Write a test that would have caught this bug
- Verify the fix with the test
- Check for other places in the codebase where the same issue could exist

## Common Pitfalls

- **Fixing symptoms** instead of root causes → always ask "why did this happen?"
- **Changing multiple things at once** → you'll never know which change fixed it
- **Skipping observation** → hypotheses without evidence are just guesses
- **Not writing a regression test** → the bug will come back

## Related Techniques

For tracing errors back to their origin: use `root-cause-tracing`
For async/timing issues: use `condition-based-waiting`
Before declaring a fix complete: use `verification-before-completion`
