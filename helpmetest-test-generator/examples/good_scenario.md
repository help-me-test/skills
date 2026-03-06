# Good Scenario Example

This is a test file to verify recursive directory sync works.

## Good Scenario Structure

```yaml
scenarios:
  - id: test-example
    description: Complete user flow with verification
    steps:
      - Navigate to /login
      - Enter email "test@example.com"
      - Click "Sign In"
      - Verify URL is /dashboard
```
