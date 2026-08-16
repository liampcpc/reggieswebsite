---
name: lead-response-tracker
description: Pull new GHL opportunities since the last run, calculate Noah's call-response speed and quote-landed commission, and update the Lead Response Tracker spreadsheet. Use when the user asks to "run the lead tracker", "update the commission sheet", "check Noah's response times", or similar.
---

# Lead Response Tracker

Updates `/Users/liampc/Documents/Reggie's/Lead Response Tracker/lead_response_tracker.xlsx` with any GHL opportunities created since the last run, computes speed-to-lead and quote-landed commission, and refreshes the Summary tab. Business location: `dHuu0Og767vhLl3YnwTF` (Reggie's Window & Gutter Cleaning).

## Business rules (do not re-derive — these were explicitly confirmed with the user on 2026-08-15)

- **Business hours:** 9:00am–6:00pm, 7 days a week, Melbourne local time. All GHL timestamps are UTC — convert by adding 10 hours (AEST, no DST in effect Jun–Sep; add 11 hours instead if the run date falls in AEDT, roughly Oct–Apr — check the current date).
- **Speed-to-Lead exclusion is anchored to when the OPPORTUNITY WAS CREATED**, not when the call happened. A lead created outside business hours is excluded from the response-time average and the $5 bonus, but still counts toward the conversion rate. (This was Claude's interpretation of the user's instruction, flagged and not yet explicitly re-confirmed — if the user ever corrects this, update this file.)
- **$5 speed bonus** requires ALL of: a logged outbound call exists, the opportunity was created within business hours, time from creation to that first call is under 7 minutes, and the lead is not marked Dud.
- **Time to Call** uses the FIRST outbound call attempt to the contact, regardless of whether it was answered (no-answer attempts count as the response).
- **$10 quote-landed bonus** triggers the first time an opportunity's pipeline stage is one of: `Quoted`, `Follow Up`, `Converted`, `Recurring Clients` (Lead Pipeline), or `Booked` (Gutter Cleaning Pipeline — its own "Quoted" stage is already covered by the shared name). Once earned, it is **locked in permanently** — if the opportunity later regresses to a worse stage, do not revoke the $10. This is why the sheet has both a live "Stage Qualifies (live)?" formula column and a separate "Quote Landed - Locked?" value column — only the locked column feeds commission.
- **One opportunity = one $10**, regardless of how many services (window/gutter) were requested together.
- **Dud leads** are marked manually by the user in the `Dud?` column on the Leads tab (Yes/No). Never auto-mark a lead as Dud yourself, even if it looks like spam — flag it in the Notes column instead and let the user decide. Once marked Dud, a row is excluded from all commission and conversion-rate math, but stays in the sheet (never delete rows).
- **Config tab** holds the qualifying-stage list and a plain-English copy of these rules — keep it in sync if any rule changes.
- **Speed to Lead section** on the Summary tab includes "% of eligible calls reached under 7 minutes" (calls under 7 min ÷ calls eligible for Speed-to-Lead, both restricted to business-hours-created, non-dud leads) — keep this alongside the raw counts, don't remove it.

## Process for each run

1. **Read the last run date** from the `Meta` sheet (hidden), cell B1, in the existing workbook. If the workbook doesn't exist yet, this is a first run — ask the user how far back to pull instead of guessing.
2. **Get pipeline stage IDs** via `mcp__ghl-mcp__opportunities_get-pipelines` if you don't already have them cached in this session — stage IDs are stable but re-verify if it's been a while, pipelines can change.
3. **Pull opportunities created since the last run date** via `mcp__ghl-mcp__opportunities_search-opportunity` with `query_date` set to the last run date (mm-dd-yyyy), `query_status=all`, `query_limit=100`, paginating with `query_startAfter`/`query_startAfterId` from the response `meta` if there are more than 100. Do this across all pipelines (don't filter by `query_pipeline_id` — pull everything, the pipeline stage mapping tells you which rules apply).
4. **For each new opportunity**, get its contact's conversations (`mcp__ghl-mcp__conversations_search-conversation` with `query_contactId`) and then the call-type messages (`mcp__ghl-mcp__conversations_get-messages` with `query_type=TYPE_CALL`) to find the first outbound call timestamp, if any.
5. **For each opportunity already in the sheet from a prior run**, re-fetch its current stage (a quick way: re-run the opportunity search for the full date range, or fetch individually via `mcp__ghl-mcp__opportunities_get-opportunity`) and update the "Stage Qualifies (live)?" column — if it now qualifies and the locked column was previously "No", flip the locked column to "Yes" (never the reverse).
6. **Write new rows** for new opportunities following the exact column layout and formulas already in the Leads sheet (open the existing file and copy the formula pattern from an existing row rather than reinventing it). Current layout (as of the 2026-08-15 rebuild — Opportunity ID and Service Category columns were removed at the user's request, don't re-add them): A=Contact Name, B=Service Type, C=Created At (Melbourne local, as an actual datetime value you compute in Python before writing), D=Within Business Hours formula, E=First Call At (Melbourne local datetime or blank), F=Time to Call formula, G=Under 7 min? formula, H=Speed Bonus $5? formula, I=Pipeline Stage (text), J=Stage Qualifies (live)? formula, K=Quote Landed - Locked? (value, not pure formula — see rule above), L=Commission formula, M=Dud? (blank/"No" for new rows — user fills in), N=Traffic Source, O=Notes.
   The "By Service Type" breakdown on the Summary tab reads the Service Type text directly (column B) via `SUMPRODUCT`/`SEARCH` — there's no separate category helper column anymore, don't recreate one.
7. **Update the Meta sheet**: set B1 (Last Run Date) to now, and consider logging B2 history if useful.
8. **Recalculate the workbook** — this is mandatory, formulas write as strings with no cached values until recalculated. A pre-patched copy of the xlsx skill's `recalc.py` (see note below) is already saved at:
   ```
   python3 "/Users/liampc/Documents/Reggie's/Lead Response Tracker/.tools/xlsx_scripts/recalc.py" "/Users/liampc/Documents/Reggie's/Lead Response Tracker/lead_response_tracker.xlsx" 90
   ```
   Note: the system Python here is 3.9, and the xlsx skill's stock `recalc.py` uses a 3.10-only `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` call that crashes on load. The saved copy above has that kwarg stripped. If the xlsx skill has since been updated and this saved copy is stale/missing, re-copy `scripts/` from the current xlsx skill install and re-patch (remove `ignore_cleanup_errors=True` from the `tempfile.TemporaryDirectory(...)` call in `recalc.py`), then overwrite the saved copy.
9. **Verify before handing off**: load the recalculated file with `openpyxl` (`data_only=True`) and sanity-check a few rows and the Summary totals against a manual spot-check, the same way the first run was verified. Never report totals you haven't checked.
10. **Send the updated file to the user** and summarize what changed since last run: new leads, new commission earned, conversion rate delta if meaningful, and call out anything that needs their judgment (a new lead that looks like spam, an old lead still sitting uncalled, etc.) — the way Carlos Felipe Rojas and Morris Chris were called out in the first run.

## Formatting note (fixed 2026-08-15)

The first version used fixed column widths that clipped long text (contact names, combined
service strings like "Window Cleaning, Gutter Cleaning", and the Notes column). When adding
rows on a future run, re-run an auto-fit pass over the Leads sheet afterward: measure the max
character length per plain-text column (Opportunity ID, Contact Name, Service Type, Pipeline
Stage, Dud?, Traffic Source) including the header, set width to that + padding (min 10, sensible
max per column), cap the Notes column width (around 55) and let it wrap with a computed row
height based on its text length — don't just reuse the widths baked into the existing file
as-is if new rows have longer content than what's already there.

## What NOT to do

- Don't hardcode computed numbers into cells — every stat on the Summary tab must be a live formula referencing the Leads tab, so the sheet stays correct if the user hand-edits a Dud flag later.
- Don't delete or renumber existing rows when adding new ones.
- Don't silently change the business-hours or commission rules above without the user explicitly asking — these have real payroll consequences.
- Don't mark anything as Dud yourself.
