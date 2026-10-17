## 2026-10-09 - [Fix insecure token generation and login timing attacks]
**Vulnerability:** The application used `uuid.uuid4()` to generate tokens for the API login endpoint, which is not cryptographically secure and vulnerable to guessing attacks. Additionally, simple equality checks were used to verify passwords, which leads to potential timing attacks.
**Learning:** Security gaps exist due to lack of the usage of the standard `secrets` Python module for critical cryptographic or authentication tasks.
**Prevention:** Always use cryptographically secure utilities like `secrets.token_urlsafe()` for tokens and `secrets.compare_digest()` for password matching.
