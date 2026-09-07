---
trigger: always_on
---

# Directives for Test Execution

- **Minimize Test Runs:** Always run the minimum possible set of critical tests necessary to validate changes. Avoid running unnecessary or full test suites.
- **Targeted Scope:** Identify and execute only the unit or integration tests directly affected by the modified code.
- **Skip for Minor Changes:** If the code modification is extremely small or superficial (e.g., typos, comments, minor formatting, variable renaming, simple UI text updates), do NOT run any tests.