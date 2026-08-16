---
name: suburb-page-builder
description: Build new suburb/location pages for Reggie's website, wire them into internal linking and the sitemap, and run a full SEO/linking audit. Use when the user asks to "build location pages", "add suburb pages", "create a page for [suburb]", or similar.
---

# Suburb Page Builder

Builds new `/locations/[suburb]` pages on the Reggie's static site, wires them into the
locations hub, sitemap and neighbouring pages' internal links, then audits the result.

Repo: `/Users/liampc/Documents/Reggie's/Website` (static HTML, no build step, deploys to
Vercel on push to `main`). Site: `reggieswindows.com.au`.

This skill supersedes `location-page-template.md` in the repo root — that file is the
original brief and is kept for reference, but this skill is the source of truth.

---

## Fixed business facts (never re-ask these)

- **Business name:** `Reggie's Window and Gutter Cleaning` — use this **exact** string in the
  JSON-LD `name` field and the nav logo `alt`. It matches the Google Business Profile listing;
  variants ("&" instead of "and", "Windows & Gutters") were cleaned up site-wide for NAP
  consistency and must not be reintroduced.
- **Phone:** 0406 981 681 · **Email:** hello@reggies.com.au · **ABN:** 42 491 259 338
- **Services:** window cleaning, gutter cleaning, solar panel cleaning, commercial
- **No fixed address.** Service-area business — schema uses `areaServed` only, never an
  `address` field. Settled decision, don't revisit per page.
- **USPs:** 500+ Melbourne homes · 5.0★ Google rating · 48hr typical booking · before/after
  photo report by SMS · streak-free guarantee (return and fix, free) · fully insured &
  background-checked · pure deionised water-fed pole system (warranty-safe) · bundle discount ·
  founder background in premium hotel facilities management ("hospitality-grade")
- **Voice:** warm, community-oriented, expert but neighbourly. No corporate filler.
- **Nav:** Residential / Commercial / Solar Panels / Gutters / Locations / About / Get Quote.
  No "Home" item (logo is the home link). `vntg-active` goes on the Locations `<li>`.

---

## Process

### 1. Confirm scope, then check for photos
Ask only if genuinely blocking. Do check `/Users/liampc/Documents/Reggie's/Website Images/`
for a photo named after the suburb — the user often drops them there without mentioning it.
If none exists, use the gradient placeholder (step 4) and say so explicitly rather than
silently shipping a placeholder.

### 2. Pick the region and identify live neighbours
Read `locations/index.html` to see which region group the suburb belongs under (Inner North /
Inner East / Inner West / North East) and which neighbouring suburbs already have live pages.
**Only ever link to suburbs that actually have a built page** — check the filesystem, don't
assume. A link to a non-existent suburb is a 404.

### 3. Build the page
Copy the newest existing page as the structural base (as of Aug 2026: `locations/thornbury.html`,
`locations/fairfield.html`) rather than writing from scratch — they carry the current template.
Replace all suburb-specific content. See "Page template" below for the required structure.

### 4. Hero image
- **Real photo available:**
  ```html
  <section class="vntg-loc-hero vntg-animate">
    <img src="/assets/img/locations/[slug]-hero.jpg" alt="[Suburb] Melbourne" class="vntg-loc-hero-img">
    <div class="vntg-loc-hero-overlay"></div>
    <div class="vntg-loc-hero-content">
  ```
  Process into `assets/img/locations/[slug]-hero.jpg` with
  `sips -Z 1920 -s formatOptions 78 "<source>" --out [slug]-hero.jpg`. **Never upscale past the
  source's native resolution** — `-Z` only shrinks, but if the source is smaller than 1920 just
  convert/compress at native size. Target well under ~500KB.
- **No photo:** keep `vntg-loc-hero-noimg` on the section (gradient placeholder), no `<img>`,
  no overlay div, and leave an HTML comment saying a real photo is still needed.

### 5. Wire in the internal linking — BOTH directions
This is the step most easily half-done. For every neighbouring suburb that has a live page:
- **New page → neighbour:** link in the hero suburb-pill bar, the intro paragraph, the
  "Already on your street" card, and the "Already in your neighbourhood" paragraph.
- **Neighbour → new page:** go edit that neighbour's page and add the reciprocal link in *its*
  hero pill bar and *its* body copy (same three spots). Skipping this leaves the new page an
  orphan that only the hub links to.

Body-copy links use `class="vntg-inline-link"`. Hero pill links are
`<a href="/locations/[slug]" class="vntg-loc-suburb-pill">Name</a>` (plain `<span>` for suburbs
with no page).

### 6. Wire into the hub page
Add `<a href="/locations/[slug]" class="opt-suburb-pill live">[Suburb] →</a>` to the correct
region group in `locations/index.html`, and remove the matching `<span class="opt-suburb-pill
soon">` placeholder if one exists.

### 7. Update the sitemap
Add `<url><loc>https://reggieswindows.com.au/locations/[slug]</loc><lastmod>YYYY-MM-DD</lastmod></url>`
to `sitemap.xml`. **This is easy to forget and it's the difference between Google finding the
page and not.** After deploying, tell the user to resubmit `sitemap.xml` in Search Console →
Sitemaps (they just re-enter `sitemap.xml` and hit Submit — there's no separate "resubmit" button).

### 8. Audit — mandatory, never skip
```bash
python3 "/Users/liampc/Documents/Reggie's/Website/.claude/skills/suburb-page-builder/audit.py"
```
Start the dev server first if it isn't running (see Gotchas). The script checks every item in
the audit list below and exits non-zero on failure. Fix everything it reports, re-run until
clean, and **report the actual output** — never claim a clean audit you didn't run.

### 9. Commit and push
One commit for the batch. Push to `main` (auto-deploys to Vercel). Then remind the user to
resubmit the sitemap in Search Console.

---

## Page template — required structure, in order

1. `<head>`: charset, viewport, `<title>`, `<meta name="description">`, favicon block
   (5 links + `theme-color`), stylesheet, JSON-LD schema
2. `<nav class="vntg-nav">` — `vntg-active` on Locations
3. `<section class="vntg-loc-hero ...">` — breadcrumb, `vntg-loc-tag` (region), H1,
   `vntg-loc-hero-sub`, two CTA buttons, `vntg-loc-suburbs-bar` (5 pills)
4. `<div class="vntg-loc-services-strip">` — 3 services
5. `<section class="vntg-loc-intro">` — "About this area", 2 paragraphs, `vntg-loc-stats` (4 cards)
6. `<div class="vntg-divider">`
7. `<section class="vntg-loc-suburb-section">` — "Built for [Suburb]'s housing mix", H2
   "Every era, treated properly.", 3 `vntg-housing-card`s, then a `vntg-checklist` of 4 items
   where **3 carry the service inline links** (`/gutters`, `/solar`, `/residential`)
8. `<div class="vntg-divider">`
9. `<section class="vntg-loc-suburb-section">` — "Why locals choose us" / "Why [Suburb] picks
   Reggie's." — 5 cards: photo-proof, streak-free guarantee, already-on-your-street (with
   neighbour links), fully insured & background-checked, bundle and save
10. `<section class="vntg-loc-testimonials">` — 2 `vntg-loc-review-card`s
11. `<div class="vntg-divider">`
12. `<section class="vntg-loc-intro">` — "Getting to you" / "Already in your neighbourhood.",
    paragraph + 3-item `vntg-checklist`
13. `<section class="vntg-faq vntg-loc-faq-soft">` — 8–10 `vntg-faq-item`s
14. `<section class="vntg-cta-wrapper">` — CTA + 3 metric cards
15. `<footer class="vntg-footer">` — includes Privacy Policy link
16. `<script src="/assets/script.js">`

### Exact patterns that must match

- **Title:** `Gutter, Window & Solar Cleaning in [Suburb] | Reggie's` — must be ≤60 chars.
  For long suburb names, shorten (e.g. drop "Solar") rather than exceed.
- **Meta description:** ≤155 chars, mention the suburb and 1–2 concrete local specifics.
- **H1:** `<h1>Gutter, Window &amp; Solar Cleaning<br>in <em>[Suburb]</em>.</h1>` — the `<em>`
  renders the suburb in brand red. Keyword-forward on purpose; do not revert to the older
  "Cleaning [Suburb] properly." branding line.
- **Schema:** `HomeAndConstructionBusiness`, `areaServed` with the suburb + 3 neighbours
  (`"[Suburb] VIC [postcode]"`), `makesOffer` ×3, `aggregateRating` 5.0/500. No `address`.
- **Footer contact line:** `[Suburb], Melbourne`

---

## Content rules

- **Real, verifiable local references only** — actual streets, parks, landmarks, housing stock.
  If you are not confident a proper noun is real, describe it generically ("the local farmers
  market"). A wrong street name is worse than a vague one. This has bitten before: a
  "Glenferrie Road" reference on the Malvern page had to be pulled for exactly this reason.
- **Proximity framing is about driving, not public transport.** Reggie's is a crew driving a
  van between jobs. Never write "easy reach from the tram" or "short trip from the station" —
  it reads like the cleaners are catching the 86. Frame it as "minutes from our regular
  [neighbour] rounds", street familiarity, and access considerations (laneways, driveways,
  body-corporate coordination).
- **Testimonials are illustrative, not verified reviews.** Keep them anonymised by street or
  area ("Clarke St. homeowner"), never invent a full name paired with a specific address.
- **Only claim neighbours you actually service.** "We already service X" where X has no page is
  fine as plain text, but don't imply a page exists by linking it.
- **Word count:** existing pages run 964–1,170 words. The original brief said 1,200–2,200; no
  page has ever hit that, and padding to reach it would mean filler. Aim for ~1,000–1,200 of
  genuinely local content and don't inflate. Flag it to the user if they want longer pages —
  that needs more real local research, not more words.

---

## Audit checklist (what `audit.py` enforces)

Per new page:
- [ ] Title present, ≤60 chars, contains the suburb
- [ ] Meta description present, ≤155 chars, contains the suburb
- [ ] H1 present, matches the keyword-forward pattern, contains the suburb
- [ ] JSON-LD present, parses as valid JSON, `name` is exactly `Reggie's Window and Gutter Cleaning`, has `areaServed`, has **no** `address`
- [ ] Favicon block + `theme-color` + manifest present
- [ ] Nav logo `alt` uses the exact business name
- [ ] All 15 required sections present in order
- [ ] Service inline links present (`/gutters`, `/solar`, `/residential`)
- [ ] FAQ count 8–10; uses `vntg-loc-faq-soft`
- [ ] Hero is either a real photo (img + overlay, image file exists) or explicitly the gradient placeholder
- [ ] Footer has the Privacy Policy link
- [ ] Word count ≥900

Site-wide:
- [ ] Every `/locations/*` href across **all** suburb pages resolves (no 404s)
- [ ] Internal linking is **bidirectional** — if A links to B, B links back to A
- [ ] New page appears in `locations/index.html` as a `live` pill
- [ ] New page appears in `sitemap.xml`
- [ ] Sitemap contains no URLs for pages that don't exist, and no page is missing from it
- [ ] No page still references the retired business-name variants

---

## Gotchas

- **Dev server:** `python3 serve.py` on port 8936 (mimics Vercel `cleanUrls`). A stale process
  from a previous session will silently 404 everything — if pages 404, kill and restart:
  `lsof -ti :8936 | xargs kill -9` then relaunch. Don't debug the routing before checking this.
- **Browser preview may be blocked by policy** for localhost. If so, verify with `curl`/Python
  and the audit script instead of screenshots — that's sufficient, don't get stuck.
- **Screenshots look blank/faded on first load** because of the `vntg-animate` scroll-in
  animation. Wait ~2s and re-screenshot, or use `get_page_text`. It is not a rendering bug.
- **Don't add tram/train references** (see Content rules) — this was a real correction.
- **Don't reintroduce** the `Opportunity ID`-style dead columns, the old
  "Cleaning [Suburb] properly." H1, or a separate service-category helper — all deliberately removed.
