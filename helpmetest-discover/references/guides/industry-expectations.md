# Industry-Based Feature Expectations

After identifying the industry, think about what a complete product in this domain needs.

## Key Questions

1. **What is the PRIMARY user goal?** (buy something, get work done, learn something)
2. **What is the CORE TRANSACTION?** (purchase, subscription, booking, submission)
3. **What steps are needed to complete that transaction from start to finish?**
4. **What would a user EXPECT to find in a product like this?**

## Expected Capabilities by Industry

### Transactional Sites (e-commerce, booking, marketplace)

**User needs:** Discover → Evaluate → Decide → Transact → Confirm

**Expected features:**
- Search
- Browse/Categories
- Product/Item Details
- Cart/Basket
- Checkout
- Payment
- Order Confirmation
- Order History

### SaaS/Productivity Tools

**User needs:** Onboard → Use Core Feature → Manage Settings → Pay

**Expected features:**
- Registration/Signup
- Dashboard
- Core Feature (the main tool)
- Settings/Profile
- Billing/Subscription

### Content/Media Platforms

**User needs:** Discover → Consume → Engage → Subscribe

**Expected features:**
- Search
- Browse/Categories
- View/Play Content
- Comments/Ratings
- Share/Social
- Subscribe/Follow

### Social Platforms

**User needs:** Profile → Connect → Share → Engage

**Expected features:**
- Profile/Account
- Feed/Timeline
- Post/Create Content
- Follow/Friend
- Messaging
- Notifications

## Discovery Process

For each expected capability:

1. **Try to find it** (check navigation, footer, user menu, follow CTAs)
2. **If found:** create Feature artifact
3. **If NOT found:** add to ProjectOverview.features with:
   ```json
   {
     "name": "<Missing Feature>",
     "status": "missing",
     "priority": "critical|high|medium|low",
     "reason": "Users cannot complete <goal> without this"
   }
   ```

## Priority Rules

- **Critical**: Blocks the core transaction
- **High**: Degrades core experience significantly
- **Medium**: Missing but workaround exists
- **Low**: Nice to have
