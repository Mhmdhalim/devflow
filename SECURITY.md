# Security

DevFlow is a learning and portfolio project, but security is treated as an engineering requirement.

- Never commit passwords, access tokens, API keys, or production secrets.
- Store local configuration in environment variables.
- Commit only safe examples such as `.env.example`.
- Validate all external input.
- Enforce authorization at the backend.
- Hash user passwords with an appropriate password hashing algorithm.
- Test authentication and permission boundaries.
- Keep dependencies updated and review automated security alerts.
