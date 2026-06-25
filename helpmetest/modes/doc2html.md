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

```robotframework
*** Settings ***
Library    Doc2HTML
Library    Browser

*** Test Cases ***
Invoice PDF contains correct total
    # Convert PDF and navigate to the rendered HTML
    Open Document    invoices/invoice-2025-01.pdf

    # Assert content using Browser keywords
    Page Should Contain    Invoice #2025-01
    Page Should Contain    Total: $1,234.56

PDF headings are preserved after conversion
    Open Document    reports/annual-report.pdf

    # Check heading structure
    ${h1}=    Get Text    h1
    Should Contain    ${h1}    Annual Report

Email attachment renders correctly
    Open Document    emails/confirmation.eml

    # Verify key fields are present
    Element Should Be Visible    css=.subject
    Page Should Contain    Order Confirmed
```

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
