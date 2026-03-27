# Phase 2.5: Coverage Analysis

**Think about what's MISSING, not just what's FOUND.**

After feature enumeration, analyze coverage gaps.

## Step 1: Identify the Core Transaction

Ask: "What does a user come here to DO?"
- **Transactional sites** (e-commerce, booking): User wants to BUY/BOOK something
- **SaaS/tools**: User wants to DO WORK with the tool
- **Content sites**: User wants to CONSUME/LEARN something
- **Social sites**: User wants to CONNECT/SHARE

## Step 2: Trace the Full Path

For the core transaction, trace every step from START to COMPLETE:

**User Goal:** What they want to achieve

**Path steps:**
- Discovery: How do they find what they need?
- Evaluation: How do they decide?
- Action: How do they take action?
- Transaction: How do they complete it?
- Confirmation: How do they know it worked?

## Step 3: Check Each Step

For each step in the path:
- Did we find a feature for this? → Link feature_id
- Is it missing? → Add to `expected_features` with priority
- Is it blocked? → Note why in `user_journeys`

## Step 4: Update ProjectOverview

Add missing features to `features` list with status="missing":

```json
{
  "name": "<Missing Feature>",
  "status": "missing",
  "priority": "critical|high|medium|low",
  "reason": "Users cannot complete <goal> without this"
}
```

Add to `user_journeys`:

```json
{
  "name": "<Goal> Flow",
  "steps": [...],
  "completion": "blocked",
  "critical": true
}
```

## Priority Rules

- **Critical**: Blocks the core transaction (no checkout = no revenue)
- **High**: Degrades core experience significantly (no search = hard to find products)
- **Medium**: Missing but workaround exists (no order history = user can check email)
- **Low**: Nice to have (no wishlist = user can remember)
