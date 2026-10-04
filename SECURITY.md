# Security

## Credentials

Never commit API keys, database credentials, tokens, private keys, production environment files, or other secrets.

Create local configuration from backend/.env.example.

## Credential rotation

A credential that was previously committed to Git should be treated as compromised even after the file is removed from the latest commit.

Rotate the affected provider credential, then remove the historical secret from repository history using the provider's recommended history-rewrite procedure.

## Runtime hardening

- Set explicit CORS origins.
- Add authentication and session ownership.
- Add request and rate limits.
- Restrict database access.
- Keep detailed exceptions in server logs rather than API responses.