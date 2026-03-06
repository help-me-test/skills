# Tag Schema

**Format:** ALL tags MUST use `category:value` format.

## Test Tags (Robot Framework)

Required: `type:X`, `priority:X`

```robot
[Tags]    type:e2e    priority:critical    feature:checkout    platform:web    scenario:happy-path
```

## Scenario Tags (in Features)

Required: `priority:X`

```json
{
  "tags": ["priority:critical", "feature:checkout", "workflow:purchase-flow", "scenario:happy-path", "project:project-evershop"]
}
```

## Allowed Categories

**Tests:** type, priority, feature, platform, browser, status, component, role, scenario
**Scenarios:** priority, feature, scenario, workflow, role, project, severity
**Features:** project, feature, priority
**Personas:** project, role

## Invalid Tags - DO NOT USE

❌ `critical` (no category)
❌ `feature_login` (wrong separator)
❌ `site:evershop` (invalid category - use `project:project-evershop`)
❌ `type:feature` (type: is for test types only)
❌ `new`, `fixed`, `temp` (meaningless)
