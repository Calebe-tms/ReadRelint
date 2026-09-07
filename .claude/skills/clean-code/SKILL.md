---
name: clean-code
description: Pragmatic coding standards. Concise, direct, no over-engineering.
when_to_use: Always active for code writing.
allowed-tools: Read, Write, Edit
version: 2.0.0
priority: CRITICAL
---
# Clean Code Rules (CRITICAL)
Be concise, direct, and solution-focused. Write code directly, fix bugs immediately, and do not write tutorials or explanations unless asked.

## 1. Principles & Structure
- Follow SRP, DRY, KISS, YAGNI, and the Boy Scout rule.
- Names: Reveal intent (userCount). Verb+noun for functions. Questions for booleans (isActive). SCREAMING_SNAKE for constants. If a name needs a comment, rename it instead.
- Functions: Max 20 lines. Do one thing. One level of abstraction. Max 3 arguments. No side effects.
- Structure: Use guard clauses (early returns). Avoid deep nesting (max 2 levels). Colocate related code.
- Anti-patterns to avoid: Obvious comments, single-use helpers/factories (inline them), magic numbers, god functions.

## 2. Mandatory Pre-Edit & Post-Edit Checks
- BEFORE EDITING: Analyze what imports the file, what it imports, test coverage, and shared components. You MUST edit the file and all dependent files in the SAME task. Never leave broken imports.
- SELF-CHECK: Before saying "task complete", verify: goal met, all files edited, code tested/works, no lint/TS errors, edge cases handled. Fix any failures before completing.

## 3. Verification Scripts Protocol
Agents must ONLY run their own scripts:
- frontend-specialist: ux_audit.py, accessibility_checker.py
- backend-specialist: api_validator.py
- mobile-developer: mobile_audit.py
- database-architect: schema_validator.py
- security-auditor: security_scan.py
- seo-specialist: seo_checker.py, geo_checker.py
- performance-optimizer: lighthouse_audit.py <url>
- test-engineer: test_runner.py, playwright_runner.py <url>
- Any agent: lint_runner.py, type_coverage.py, i18n_checker.py

## 4. Script Execution Rule (READ -> SUMMARIZE -> ASK)
1. Run script and capture ALL output.
2. Summarize output format: 
   ## Script Results: [name]
   ### Errors (X items): - [File:Line] description
   ### Warnings (Y items): - [File:Line] description
   ### Passed (Z items)
   Should I fix the errors?
3. WAIT for user confirmation before fixing. NEVER auto-fix. Re-run after fixing.