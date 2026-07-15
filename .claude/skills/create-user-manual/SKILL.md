---
name: create-user-manual
description: "Generate an end-user manual in Markdown by driving the app live with Playwright MCP and capturing a screenshot at every step. Trigger whenever the user asks for a 'user manual', 'panduan pengguna', or documentation of 'cara guna' a feature/page — e.g. 'buat user manual guna playwright untuk feature kupon', 'generate manual macam mana nak checkout', 'dokumentasikan flow login jadi panduan pengguna', or 'buatkan step-by-step guide untuk admin tambah produk'. Also trigger right after a manual Playwright MCP walkthrough when the user says something like 'ok, jadikan ni user manual' rather than a test script (that's playwright-mcp-test-generator's job, not this one). Do NOT use this for turning an MCP session into an automated test spec, and do NOT use it for internal/technical docs aimed at developers — this skill writes for non-technical end-users."
---

# Create User Manual (Playwright MCP)

## What this is for

Produce a Markdown user manual that a non-technical end-user could follow to actually use a
feature — written in plain Bahasa Melayu, one step per screenshot, no jargon. The manual's
credibility comes from the screenshots being real: every image is captured live by driving the
actual running app through Playwright MCP, not mocked up or described from memory.

This is different from `playwright-mcp-test-generator`: that skill turns a session into an
automated test (assertions, locators, pass/fail). This skill turns a session into a
human-readable how-to guide (screenshots, numbered steps, plain language).

## Step 1 — Confirm scope before touching the browser

Figure out exactly which feature/flow to document and who the audience is (e.g. "pelanggan buat
checkout" vs "admin tambah kupon"). If the user's request is vague ("buat manual untuk app ni"),
ask which specific feature or flow — a manual that tries to cover the whole app in one pass
usually ends up shallow and unfocused on every step. If the user already walked through a flow
earlier in this conversation using `mcp__plugin_playwright_playwright__browser_*` tools and says
something like "buat manual dari apa yang kita explore tadi", reconstruct the flow from that
session instead of re-navigating from scratch (same technique as
`playwright-mcp-test-generator`'s Step 1: read the tool calls in order, cross-check
`.playwright-mcp/` for exact page state).

## Step 2 — Resolve the URL

Use the `get-absolute-url` Boost tool to get the correct Herd URL for the page(s) involved — never
guess or hardcode `http://localhost` or a port. This app runs on Herd, not a manually-started dev
server.

## Step 3 — Walk the flow, screenshotting every meaningful step

For each step of the flow:

1. `browser_navigate` / `browser_click` / `browser_type` / `browser_fill_form` / `browser_select_option`
   to perform the one user action this step is documenting.
2. `browser_snapshot` to confirm the page landed in the expected state (this also gives you the
   exact visible text to describe the step accurately — don't paraphrase from guesswork).
3. `browser_take_screenshot` to capture that state. Save with a descriptive, ordered filename
   (`01-login-page.png`, `02-isi-emel-katalaluan.png`, ...) — the order must match the manual's
   step numbering so screenshots and text never drift apart if steps get reordered later.

A "meaningful step" is one decision or action the end-user takes (click a button, fill a field,
land on a new page, see a confirmation/error) — not every internal MCP call. Skip steps that are
purely incidental to automation (e.g. an intermediate `browser_wait_for`) unless the user would
actually see something change on screen at that point.

If a step can fail or branch (e.g. validation error, empty state), consider capturing that too as
a short "Jika berlaku ralat" aside — a manual that only shows the happy path leaves users stuck
the moment something looks different from the screenshot.

## Step 4 — Organize output on disk

- Markdown file: `docs/user-manual/<feature-kebab-case>.md`
- Screenshots: `docs/user-manual/<feature-kebab-case>/images/`, referenced from the markdown with
  relative paths (`images/01-login-page.png`) so the manual is portable if the docs folder moves.
- Create the folders if they don't exist yet; don't scatter screenshots into the repo root.

## Step 5 — Write the manual

Use this structure:

```markdown
# Panduan Pengguna: <Nama Feature>

## Pengenalan
<1-2 ayat: apa feature ni buat dan untuk siapa>

## Langkah-langkah

### Langkah 1: <Tindakan pengguna>
<Arahan ringkas, ayat mudah, tiada jargon teknikal>

![<Alt text describing the screenshot>](images/01-....png)

### Langkah 2: ...
...
```

Writing rules:
- Bahasa Melayu, mesra dan mudah faham — tulis macam explain kat orang yang baru pertama kali
  guna sistem ni, bukan kepada developer. Elak istilah teknikal (contoh: guna "klik butang Simpan"
  bukan "submit form").
- Setiap langkah = satu tindakan + satu screenshot. Jangan gabung banyak tindakan dalam satu
  langkah — itu punca pengguna hilang arah bila screenshot tak match dengan apa yang mereka buat.
- Describe what the user should look for in the screenshot (a button name, a field label) using
  the exact text seen in the `browser_snapshot`, not a rephrased guess.
- End with a short "Selesai" / hasil akhir yang dijangka, so the user knows they completed the
  flow correctly.

## Step 6 — Clean up and report

Close the browser (`browser_close`) when the walkthrough is done. Per this project's standing
instruction, always finish with a short summary in Bahasa Melayu of the steps taken and the
result: which feature was documented, how many steps/screenshots, and the file path to the
generated manual.
