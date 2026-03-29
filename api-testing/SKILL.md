---
name: api-testing
description: "HelpMeTest API library — write Robot Framework tests that make HTTP requests through the browser session (auth cookies included automatically). Use when user wants to test REST APIs, write API tests, chain requests, assert JSON fields, test CRUD flows, debug a failing API call, or use keywords like GET/POST/PUT/PATCH/DELETE/CURL. Triggers on: 'test the API', 'call this endpoint', 'check the response', 'POST /api/...', 'GET /api/...', 'write api tests', 'assert json', 'api returns 4xx', 'why is /api/x returning 401', 'debug this api call'. Also self-invokes when another test reveals an API call returning an unexpected status and you want to investigate or reproduce it in isolation."
allowed-tools: mcp__helpmetest-*
---

# API Testing with HelpMeTest

The API library runs HTTP requests inside the active browser tab. This means the browser's session cookies, auth headers, and credentials are sent automatically — no token juggling.

A live httpbin instance is available for examples and exploration: `https://httpbin.playground.helpmetest.com`

## The Golden Rule

Authenticate with `As  <StateName>` FIRST, then make API calls. The browser session carries everything.

```robot
As    Admin
Go To    https://app.example.com
GET    /api/users
Response Status Should Be    200
```

Never re-authenticate inside a test. Never manually copy tokens. The browser already has them.

## HTTP Verbs

### GET

```robot
Go To    https://httpbin.playground.helpmetest.com
GET    /get
Response Status Should Be    200
Field Should Exist    url

GET    /get    headers={"X-Custom-Header": "hello"}
Field Should Exist    headers.X-Custom-Header
```

### POST

```robot
Go To    https://httpbin.playground.helpmetest.com
POST    /post    body={"name": "Alice", "role": "editor"}
Response Status Should Be    200
Field Equals    json.name    Alice
Field Equals    json.role    editor
```

### PUT / PATCH

```robot
PUT    /put    body={"name": "Alice Updated"}
Response Status Should Be    200
Field Equals    json.name    Alice Updated

PATCH    /patch    body={"email": "new@example.com"}
Response Status Should Be    200
Field Equals    json.email    new@example.com
```

### DELETE

```robot
DELETE    /delete
Response Status Should Be    200
```

### POST Form (application/x-www-form-urlencoded)

```robot
POST Form    /post    fields={"username": "alice", "password": "secret"}
Response Status Should Be    200
Field Equals    form.username    alice
```

### POST Multipart (file upload)

```robot
# File on disk
POST Multipart    /post    files={"avatar": "/tmp/photo.png"}
Response Status Should Be    200

# Inline base64 — no file on disk needed
POST Multipart    /post
...    fields={"title": "Report"}
...    files={"file": {"base64": "SGVsbG8gV29ybGQ=", "filename": "hello.txt", "content_type": "text/plain"}}
Response Status Should Be    200
Field Should Exist    files.file
```

### CURL — paste directly from DevTools

```robot
CURL    curl 'https://httpbin.playground.helpmetest.com/get' -H 'X-My-Header: test'
Response Status Should Be    200
Field Should Exist    headers.X-My-Header
```

Right-click any network request in DevTools → "Copy as cURL" → paste. The library replaces the cookies in the copied command with the live browser session automatically.

## URL Rules

- **Relative** `/api/users` — resolved against the current page origin. The browser must already be at the target site (via `Go To` or `As`).
- **Absolute** `https://httpbin.playground.helpmetest.com/get` — works from any page, no prior navigation needed.
- **Same-origin APIs** — use relative URLs after navigating to the app; no CORS concerns.
- **Cross-origin APIs** — use absolute URLs; the server must allow `credentials: include` CORS requests.

## Asserting the Response

### Status

```robot
Go To    https://httpbin.playground.helpmetest.com
GET    /status/200
Response Status Should Be    200

GET    /status/404
Response Status Should Be    404

GET    /status/500
Response Status Should Be    500
```

### Body text (raw string match)

```robot
GET    /get
Response Body Should Contain    "url"
Response Body Should Not Contain    error
```

### Partial object match (Karate-style)

Checks that the response *contains* the expected structure. Extra fields are ignored.

```robot
GET    /get
Response Body Should Match    {"url": "#string", "headers": "#object"}

POST    /post    body={"name": "Alice"}
Response Body Should Match    {"json": {"name": "Alice"}, "url": "#string"}
```

Type placeholders:
| `#string`  | any string (including empty)     |
| `#number`  | any integer or float             |
| `#boolean` | true or false                    |
| `#array`   | any JSON array                   |
| `#object`  | any JSON object                  |
| `#null`    | JSON null                        |
| `#notnull` | any non-null value               |
| `#present` | key exists (value may be null)   |
| `#ignore`  | skip this field entirely         |

### Field assertions (dot-path)

Navigate nested JSON with `.` and array indices with `.N`:

```robot
GET    /get    headers={"X-App": "myapp"}
Field Equals    headers.X-App    myapp
Field Should Exist    headers.Host
Field Should Not Exist    headers.X-Nonexistent

POST    /post    body={"score": 42, "tags": ["a", "b", "c"]}
Field Equals    json.score    42
Field Equals    json.tags.0    a
Field Equals    json.tags.2    c
Field Greater Than    json.score    0
Field Less Than    json.score    100
Field Greater Or Equal    json.score    42
Field Less Or Equal    json.score    42

POST    /post    body={"message": "hello world"}
Field Contains    json.message    hello
Field Not Contains    json.message    error
Field Starts With    json.message    hello
Field Ends With    json.message    world

POST    /post    body={"uuid": "abc-123-def"}
Field Matches Regexp    json.uuid    ^[a-z]+-\\d+-[a-z]+$

POST    /post    body={"status": "active"}
Field Should Be One Of    json.status    active,pending,inactive
```

### Field type checks

```robot
POST    /post    body={"name": "Alice", "score": 99, "active": true, "tags": [], "meta": {}}
Field Type Should Be    json.name    string
Field Type Should Be    json.score    number
Field Type Should Be    json.active    boolean
Field Type Should Be    json.tags    array
Field Type Should Be    json.meta    object
```

### Array and string length

```robot
POST    /post    body={"tags": ["a", "b", "c"]}
Field Length Should Be    json.tags    3

POST    /post    body={"items": []}
Field Should Be Empty    json.items

POST    /post    body={"items": [1, 2]}
Field Should Not Be Empty    json.items
```

When the response root is an array, use `${EMPTY}` as the field path:

```robot
# hypothetical endpoint returning a JSON array
GET    /json-array-endpoint
Field Length Should Be    ${EMPTY}    5
Field Each Should Match    ${EMPTY}    {"id": "#number"}
```

### Array item matching

Assert every item in an array matches a pattern:

```robot
POST    /post    body={"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
Field Each Should Match    json.users    {"id": "#number", "name": "#string"}
```

### Empty / not empty

```robot
POST    /post    body={"errors": [], "data": [1, 2, 3]}
Field Should Be Empty    json.errors
Field Should Not Be Empty    json.data
```

### Response headers

```robot
GET    /response-headers?Content-Type=application/json
Response Header Should Be    content-type    application/json
Response Header Should Contain    content-type    json
```

### Response time

```robot
GET    /get
Response Time Should Be Less Than    2000

# httpbin /delay/N endpoint adds N seconds — use to test timeout thresholds
GET    /delay/1
Response Time Should Be Less Than    3000
```

## Extracting Values to Chain Requests

`Get Response Field` returns a value for use in the next request — the standard pattern for dependent calls.

```robot
POST    /post    body={"name": "Alice"}
Response Status Should Be    200
${name}=    Get Response Field    json.name
# ${name} == "Alice"

GET    /get    headers={"X-Echo": "${name}"}
Field Equals    headers.X-Echo    Alice
```

```robot
${status}=    Get Response Status
${body}=      Get Response Body
Log    ${body}
```

## Standard CRUD Pattern

The typical shape for testing any CRUD resource:

```robot
*** Test Cases ***
Create Read Update Delete User
    As    Admin
    Go To    https://app.example.com

    # Create
    POST    /api/users    body={"name": "Alice", "role": "editor"}
    Response Status Should Be    201
    ${id}=    Get Response Field    id

    # Read
    GET    /api/users/${id}
    Field Equals    name    Alice
    Field Equals    role    editor

    # Update
    PATCH    /api/users/${id}    body={"name": "Alice Updated"}
    Response Status Should Be    200
    Field Equals    name    Alice Updated

    # Delete
    DELETE    /api/users/${id}
    Response Status Should Be    204

    # Verify gone
    GET    /api/users/${id}
    Response Status Should Be    404
```

## Error Scenarios

Always test the unhappy paths:

```robot
Go To    https://httpbin.playground.helpmetest.com

# 404
GET    /status/404
Response Status Should Be    404

# 500
GET    /status/500
Response Status Should Be    500

# App-level: missing required field
As    Admin
Go To    https://app.example.com
POST    /api/users    body={"role": "editor"}
Response Status Should Be    400
Field Should Exist    error

# Unauthorized (no session)
GET    /api/admin/secrets
Response Status Should Be    401

# Forbidden (wrong role)
As    RegularUser
POST    /api/admin/users    body={"name": "Bob"}
Response Status Should Be    403
```

## Common Pitfalls

**Don't use Javascript fetch in tests.** The API library exists precisely so you don't have to. `Javascript    fetch(...)` bypasses auth, skips rrweb recording, and produces brittle tests.

**Relative URLs require the browser to be at the site.** Always pair with `As  <StateName>` + `Go To` at the top. Without navigation, the relative URL resolves against whatever origin the browser last visited.

**Body is a JSON string.** Pass `body={"key": "value"}` as a literal — Robot Framework passes it through as-is. The library serializes Python dicts automatically, but always write the body as a JSON string literal in tests.

**httpbin echoes what you send.** When testing against `httpbin.playground.helpmetest.com`, JSON body fields come back under `.json`, form fields under `.form`, files under `.files`, and query params under `.args`. So `POST /post body={"name":"Alice"}` → assert `json.name`, not `name`.
