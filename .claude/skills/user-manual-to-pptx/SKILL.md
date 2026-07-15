---
name: user-manual-to-pptx
description: "Turn a Markdown user manual (typically one produced by the create-user-manual skill, with numbered 'Langkah' steps and screenshots) into a real Microsoft PowerPoint deck (.pptx) that opens in PowerPoint/Google Slides/Keynote — one slide per step or group of steps, screenshot alongside plain-language bullets. Trigger whenever the user asks to turn a user manual, panduan pengguna, or step-by-step guide into 'powerpoint', 'pptx', 'slide', 'slaid', or 'persembahan' — e.g. 'dari user manual ni, buat slide powerpoint', 'jadikan manual kupon ni jadi pptx', 'export panduan ni ke slide untuk taklimat staf'. Also trigger right after create-user-manual finishes if the user follows up with 'jadikan slide' / 'buat pptx' without repeating the file path — reuse the manual that was just generated. Do NOT use this for generating the user manual itself (that's create-user-manual's job) and do NOT use it for turning arbitrary/unstructured Markdown into slides unless it's genuinely a step-by-step manual with screenshots."
---

# User Manual → PowerPoint

## What this is for

Take an existing step-by-step Markdown user manual (title, intro, numbered "Langkah" steps each
with a screenshot, closing summary — the shape `create-user-manual` produces) and turn it into a
real `.pptx` file people can open in PowerPoint and present or hand out. The manual's prose is
usually too dense for a slide, so this isn't a copy-paste job: it's a compression job. Slides are
skimmed in seconds, not read line by line, so each one needs the screenshot to visually dominate
and the text trimmed to what someone needs while glancing at the screenshot.

## Step 1 — Find and read the source manual

If the user just finished running `create-user-manual` in this conversation, use that output
directly — don't ask them to re-paste the path. Otherwise, locate the `.md` file they mean (ask if
ambiguous). Read it fully, and also open its `images/` folder to confirm the screenshots it
references actually exist on disk — a slide with a missing image is worse than no slide.

## Step 2 — Decide how steps map to slides (the judgment call)

Don't default to one slide per step. Read the manual like a person about to present it: some steps
are substantial (a form with six fields, a decision point) and deserve a full slide with the
screenshot dominant and their own bullets. Others are small connective steps (click a nav link,
confirm a success toast, type into a search box) that say very little on their own and read fine
two-or-three-to-a-slide, each getting its own screenshot in a smaller side-by-side column. Grouping
purely by position (every 2 steps) produces awkward slides where an important step gets shrunk
next to a trivial one — group by *what the audience actually needs to stop and look at*.

As a rule of thumb: if a step's screenshot shows a filled form, an error state, or something the
audience needs to study, give it its own slide. If it just confirms something happened or performs
a simple navigation click, it's a good candidate to combine with its neighbor.

Also condense the wording. The manual's Bahasa Melayu instructional prose (e.g. "Buka pautan sistem
dan masukkan emel serta kata laluan akaun staf anda, kemudian klik butang 'Log in'.") becomes 2-3
short bullet fragments on a slide, not a full sentence carried over verbatim — a slide bullet is a
prompt for the presenter to speak from, not a paragraph to be read silently.

## Step 3 — Write the slide spec JSON

Translate your grouping decision into a JSON file matching this schema, then hand it to the
rendering script — don't hand-write PowerPoint XML or improvise a different Python approach, the
script in `scripts/build_pptx.py` already handles layout, image scaling/centering, and a consistent
visual theme:

```json
{
  "title": "Panduan Pengguna: <Nama Feature>",
  "subtitle": "Optional context line (module name, audience)",
  "footer": "Text repeated in the corner of every slide",
  "intro_bullets": ["2-4 short lines summarizing what the feature does and who it's for"],
  "slides": [
    {
      "heading": "Slide title for one substantial step",
      "layout": "single",
      "image": "relative/path/to/screenshot.png",
      "bullets": ["short fragment", "short fragment"]
    },
    {
      "heading": "Slide title covering 2-3 minor steps grouped together",
      "layout": "combined",
      "items": [
        {"label": "Langkah 3", "text": "one short line", "image": "relative/path.png"},
        {"label": "Langkah 4", "text": "one short line", "image": "relative/path.png"}
      ]
    }
  ],
  "closing_bullets": ["1-3 lines wrapping up what the audience can now do"]
}
```

- `layout: "single"` — one large screenshot (auto-scaled, centered) beside a bullet list. Use for
  any step that deserves full attention.
- `layout: "combined"` — 2-3 side-by-side mini-columns, each with its own small screenshot and one
  short caption. Use for minor/connective steps. Don't put more than 3 items in one `combined`
  slide — beyond that the screenshots become too small to read.
- Image paths are resolved relative to the manual's own folder (same relative paths the Markdown
  file already uses), so you can copy them straight from the manual's `![alt](path)` syntax.

Save this JSON to a temp/working location (the skill's scratch use is fine) — it's an intermediate
artifact, not a deliverable, so don't worry about it looking polished.

## Step 4 — Render the deck

Run the script from the repo root (or pass absolute paths):

```bash
python .claude/skills/user-manual-to-pptx/scripts/build_pptx.py <slides.json> <output.pptx> --base-dir <manual's-folder>
```

`--base-dir` must point at the folder the image paths in the JSON are relative to — normally the
same folder the source `.md` file lives in (e.g. `docs/user-manual/`), since manual images are
referenced like `pengurusan-kupon/images/01-....png`.

If a referenced image is missing, the script renders a visible placeholder box instead of failing
silently — check the script's stdout and the deck itself for any `[imej tiada: ...]` placeholders
before calling the job done; that means a path in your JSON didn't match reality.

The script requires `python-pptx` and `Pillow` (already used for image dimension lookup). If a
fresh environment doesn't have them: `pip install python-pptx pillow`.

## Step 5 — Save and report

Save the `.pptx` next to the source manual (e.g. `docs/user-manual/<feature>.pptx`) unless the user
asked for somewhere else. Confirm the file exists and report: how many slides, which steps got
combined and why (briefly), and the file path — in Bahasa Melayu to match this project's
convention, unless the user has been writing in English.
