# Location Page Generation — Reusable Template
Reggie's Window & Gutter Cleaning

> **SUPERSEDED (Aug 2026).** The working process now lives in the `suburb-page-builder` skill
> (`.claude/skills/suburb-page-builder/`), which carries the current page template, the exact
> markup patterns, content rules learned since this doc was written, and a runnable `audit.py`
> that mechanically checks SEO, headings, bidirectional internal linking, hub-page wiring and
> sitemap coverage. Use the skill. This file is kept for the original SEO-brief format and
> background reasoning only.

This is the standing brief for generating new suburb/location pages (~3 per week). Reference this document each time instead of re-deriving the approach from scratch. It is not suburb-specific — replace `[SUBURB]` and the bracketed prompts below with the real details each time.

---

## Fixed business facts (do not re-ask these each time)

- **Business:** Reggie's Window & Gutter Cleaning ("Reggie's Windows & Gutters")
- **Phone:** 0406 981 681 · **Email:** hello@reggies.com.au
- **Services:** Residential window cleaning, gutter cleaning, solar panel cleaning, commercial cleaning
- **No fixed address.** Reggie's is a mobile, service-area business (SAB) — never invent a storefront address. Schema uses `areaServed` only (see template below). This was an explicit decision, not a gap — don't second-guess it per page.
- **USPs to draw on:** 500+ Melbourne homes serviced · 5.0★ Google rating · 48hr typical booking turnaround · before/after photo report via SMS on every job · streak-free guarantee (return and fix, no charge) · fully insured & background-checked · pure deionised water-fed pole system for solar (no chemicals, warranty-safe) · bundle discount for multiple services in one visit · founder background in premium hotel facilities management ("hospitality-grade" standard)
- **Brand voice:** warm, community-oriented, expert but neighbourly. No generic corporate speak. Matches the tone already used across the site's existing suburb pages (Ascot Vale, Malvern, Ivanhoe, Brunswick).
- **Nav structure:** Residential / Commercial / Solar Panels / Gutters / Locations / About / Get Quote — no "Home" nav item (logo is the home link).
- **Locations hub:** `/locations` groups suburbs by region (Inner North / Inner East / Inner West / North East, etc.). Check the hub page for which region a new suburb belongs under, and which neighbouring suburbs are already live vs. "coming soon" — only link to suburbs that actually have a built page.

---

## Process — follow in this order

### 1. Ask only if genuinely blocking
Don't re-ask about the address/schema approach (settled: no address). Do ask if:
- The suburb's region grouping isn't obvious (which existing hub region does it belong under, or is it a new region?)
- You want a specific service emphasis for that suburb, or even weighting (default: even weighting across all 3 services, matching the site pattern)
- Real photos exist for that suburb — check the GHL-sourced media library first (Ascot Vale, Malvern, Ivanhoe, Brunswick have real photos from the original site; any suburb outside those 4 almost certainly has no real photo). If none exist, say so explicitly and offer the branded-gradient hero as the placeholder rather than guessing with a stock image — this is not something to silently work around.

### 2. Produce the SEO content deliverable, in this format:

```
## Hyperlocal Intent Analysis
## Page Outline
## Full Page Content
## On-Page SEO & Schema Recommendations
```

- **Hyperlocal Intent Analysis:** 2–3 realistic searcher segments for that suburb (usually maps to: heritage/established-home owners, renovators, and a suburb-specific angle — solar density, coastal salt air, bushfire-zone gutter risk, etc. — whatever is actually true of that suburb). Explicitly address how relevance is proven without a fake address (proximity to already-serviced neighbouring suburbs + accurate local landmark/housing-stock references, not suburb-name-dropping).
- **Page Outline:** H1–H3 outline, local-first: intro → local pain-point/hook → housing-mix or service-tailoring section → why locals choose us → FAQ → CTA. Reuse the same section shape as the Northcote brief unless the suburb's story genuinely calls for something different.
- **Full Page Content:** 1,200–2,200 words. Use **real, verifiable local references** (actual streets, parks, transit lines, landmarks) — never invent a market/event/venue name you're not confident is real. If unsure of a specific proper noun, describe generically (e.g. "the local farmers market") rather than assert a name that could be wrong.
- **On-Page SEO & Schema Recommendations:** SEO title (≤60 chars), meta description (≤155 chars), schema (no address field — see JSON template below), 4–6 image alt texts, 5–7 internal link suggestions.

### 3. Build the actual page — and this time, implement the internal links
The Northcote build skipped step 3 of its own recommendations — the SEO brief listed internal-link suggestions, but they never made it into the HTML. **Don't repeat that.** Every page must actually include, in the body copy (not just nav/footer):
- First mention of gutter-related content → `<a href="/gutters" class="vntg-inline-link">`
- First mention of window-related content → `<a href="/residential" class="vntg-inline-link">`
- First mention of solar-related content → `<a href="/solar" class="vntg-inline-link">`
- Mention of a neighbouring suburb that already has a live page → `<a href="/locations/[suburb]" class="vntg-inline-link">` (only if that page actually exists — check first)
- CTA(s) → `/quote` (already standard in every template button)
- "View all locations" → `/locations` (already standard)

The `.vntg-inline-link` class (red, underlined, hover state) is already defined in `assets/styles.css` — reuse it, don't redefine per page.

### 4. Match the established visual template
The finalized suburb-page template (as of Northcote) is the **original page structure** — `vntg-loc-hero` (real photo if available, otherwise the `vntg-loc-hero-noimg` branded-gradient placeholder — see step 1), `vntg-loc-services-strip`, `vntg-loc-intro`, `vntg-loc-suburb-section` — **with two style swaps and one removal**:
- **Testimonials:** use the "soft modern" markup — `<section class="vntg-loc-testimonials vntg-animate">` containing `.vntg-loc-testimonials-label`, an `<h2>`, and a `.vntg-loc-review-grid` of `.vntg-loc-review-card` items (star rating, italic quote, `.vntg-loc-review-avatar` initial circle + name/suburb). Not the older `vntg-testimonials`/`vntg-review-card` markup.
- **FAQ:** keep the standard `vntg-faq`/`vntg-faq-item`/`vntg-faq-question`/`vntg-faq-answer` structure and JS (`vntgToggleFaq`) unchanged, but add `vntg-loc-faq-soft` as an extra class on the `<section class="vntg-faq ...">` wrapper for the rounded-card soft-modern visual treatment.
- **Remove entirely:** the `vntg-locations` "Where else do we service?" section (map graphic + "View all locations" link block). If it contained a neighbouring-suburb mention worth keeping for internal linking (step 3), fold that sentence into the `vntg-loc-intro` paragraph instead of dropping the link.

All three style rules live in `assets/styles.css` already (`.vntg-loc-testimonials*`, `.vntg-loc-faq-soft`) — reuse them, don't redefine per page. Don't re-run the "3 aesthetic mockups" exploration for every new suburb — that was a one-time exercise to pick this direction. Only revisit aesthetics if explicitly asked to. New pages should look like siblings of Brunswick/Malvern/Ivanhoe/Northcote, not one-off designs.

### 5. Wire it in
- Add the new suburb's link to the correct region group on the `/locations` hub page (replacing its "coming soon" placeholder if it had one).
- Update the nearby/"coming soon" suburb lists on adjacent suburb pages if relevant.

### 6. Verify before handing off
- No console errors, no horizontal overflow at desktop width (test ~1000px and ~1300px, since that's where nav-overflow bugs have shown up before)
- All internal links resolve to real pages (or are left as plain text if the target doesn't exist yet)
- FAQ count 8–10, testimonials illustrative and clearly written in the same voice as existing pages (not presented as verified reviews)

---

## Schema template (copy and adapt per suburb)

```json
{
  "@context": "https://schema.org",
  "@type": "HomeAndConstructionBusiness",
  "name": "Reggie's Window & Gutter Cleaning",
  "telephone": "+61406981681",
  "email": "hello@reggies.com.au",
  "areaServed": [
    { "@type": "Place", "name": "[SUBURB] VIC [POSTCODE]" },
    { "@type": "Place", "name": "[Neighbouring suburb 1] VIC [POSTCODE]" },
    { "@type": "Place", "name": "[Neighbouring suburb 2] VIC [POSTCODE]" }
  ],
  "makesOffer": [
    { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Window Cleaning" } },
    { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Gutter Cleaning" } },
    { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Solar Panel Cleaning" } }
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "5.0",
    "reviewCount": "500"
  }
}
```
*No `address` field — deliberate, per Google's guidance for service-area businesses without a public storefront.*

---

## Reference example
See `locations/northcote.html` (built page, using the finalized template from step 4) and the original `northcote-seo-brief.md` (superseded by this template, kept for reference) for a worked example of the full process.
