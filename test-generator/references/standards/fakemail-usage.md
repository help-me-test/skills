# FakeMail Keywords

For registration and email verification tests, use FakeMail.

## Basic Usage

```robot
# Generate unique test email
${email}=  Create Fake Email
# Returns: adventure.acme@fakemail.helpmetest.com

# Use in registration
Fill Text  input[name=email]  ${email}
Click  button >> "Register"

# Get verification code from email
${code}=  Get Email Verification Code  ${email}
Fill Text  input[name=code]  ${code}

# Cleanup after test
Delete Email  ${email}
```

## Critical Rule

**NEVER hardcode emails** - always use `Create Fake Email`.

## Why FakeMail?

- Unique email for each test run
- No conflicts between test runs
- Verification codes retrievable
- Automatic cleanup possible
- No external email service dependencies
