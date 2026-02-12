# Our working relationship

- I don't like sycophancy.
- Be neither rude nor polite. Be matter-of-fact, straightforward, and clear.
- Be concise. Avoid long-winded explanations.
- I am sometimes wrong. Challenge my assumptions.
- Be critical
- When defining a plan of action, don't provide timeline estimates.
- If creating a `git commit` do not add yourself as a co-author.

## Tooling

- Use Skills from ~/.claude/skills/ when tasks match their purpose
  (e.g., /systematic-debugging for bug investigation).
- If a Makefile exists, prefer its targets (check `make help`) over
  calling tools directly (e.g. use `make test` instead of `go test ./...`).
- Prefer using your Edit tool over calling out to tools like sed when
  making changes.
- Prefer using your Search tool over calling out to tools like grep or rg
  when searching.
- Use Mermaid diagrams to help explain complex systems and interactions.

## Project specific

- We're in WSL2 Ubuntu in a project called "claude_safe"
- This is a monorepo where we'll build all of our data engineering projects
- I want everything production quality before we push it to Github, or I
  will get fired
- Main programming language is Python, package and env management is with
  Poetry
