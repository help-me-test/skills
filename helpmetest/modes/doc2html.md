<!-- llms-description: Convert PDF, DOCX, EPUB, email and Markdown to HTML and assert on the rendered content. -->

# HelpMeTest Doc2HTML Mode

Convert documents (PDF, DOCX, EPUB, EML, MD, and more) to HTML and assert their rendered content using Browser keywords. Uses the `Doc2HTML` library.

---

## Trigger

```
/helpmetest doc2html            # test document rendering
/helpmetest document <task>     # alias — e.g. "test the PDF viewer", "verify converted document"
```

Triggers on: PDF, DOCX, Word file, document, convert doc, Open Document, EPUB, EML.

---

## Keywords

### Open Document (convert + navigate in one step)

```robotframework
Open Document    path/to/file.pdf          # convert and navigate browser to the HTML
Open Document    path/to/file.docx
Open Document    https://example.com/doc.pdf    # also accepts URLs
```

After `Open Document`, the browser is on the rendered HTML page — use any Browser/Playwright keyword to assert content.

### Convert Document (convert only, no navigation)

```robotframework
${html_path}=    Convert Document    path/to/file.pdf     # returns local HTML path
${html_path}=    Convert Document    path/to/file.docx
```

Use when you need the HTML path for further processing before navigating.

---

## Supported formats

| Extension | Format |
|-----------|--------|
| `.pdf` | PDF |
| `.docx` / `.doc` | Microsoft Word |
| `.epub` | EPUB e-book |
| `.eml` / `.msg` | Email message |
| `.md` | Markdown |
| `.html` / `.htm` | HTML (pass-through) |
| `.txt` | Plain text |

---

## Example test

A HelpMeTest test body is **bare keywords with comments** — no `*** Settings ***`, no
`Library` lines, no `*** Test Cases ***` header, no indentation. The libraries are already
loaded for you. Verified 2026-09-25: of the 143 tests in a live workspace, **zero** contain
a `*** Settings ***` section, and the two passing doc2html tests look like this:

```robotframework
# Download public PDF via URL and verify content
Open Document  https://arxiv.org/pdf/gr-qc/9905021
Find  Bel
```

```robotframework
# Unsupported file → must be rejected with HTTP 415
# single assertion by design: the only contract is the error code
Run Keyword And Expect Error    *415*    Convert Document    /app/libraries/Doc2HTML/tests/corpus/unsupported.bin
```

So a new one is written the same way — one test per `helpmetest test create`, the body
being the keywords alone:

```robotframework
# Convert the invoice PDF and land on the rendered HTML
Open Document  invoices/invoice-2025-01.pdf

# The totals a finance user actually checks
Browser.Get Text  body  *=  Invoice #2025-01
Browser.Get Text  body  *=  Total: $1,234.56
```

**Measured behaviour of `Open Document`**, which the section above does not spell out: it
converts, writes the HTML under `/tmp/doc2html_output/<hash>/index.html`, **navigates the
browser there itself** (an implicit `Go To file://…` appears in the output), and returns
that path. After it, plain Browser keywords work against the rendered page — a live run on
a remote PDF returned `Dummy PDF file` from `Get Text  body`.

---

## Workflow

1. Orient: `helpmetest status` + `helpmetest artifact list`
2. Identify the document(s) to test and what to assert (text, structure, images)
3. Write the test using `Open Document` + Browser assertion keywords
4. `helpmetest test create --id <id> --name "<name>" --file <file>` to push it
5. `helpmetest test run --id <id>` to execute
6. Report pass/fail with the specific assertion that failed if any

---

## Notes

- `Open Document` is the primary keyword — use `Convert Document` only when you need the HTML path
- After `Open Document`, all standard Browser/Playwright keywords work normally
- For email flows that produce a PDF attachment: chain `fakemail` → `doc2html`
- Large PDFs may take a few seconds to convert — the keyword waits automatically
