#!/usr/bin/env python3
"""
Audit every suburb page on the Reggie's site.

Checks per-page SEO/structure and site-wide linking/sitemap consistency.
Filesystem-based — does not require the dev server to be running.

Usage:
    python3 audit.py                # audit all suburb pages
    python3 audit.py fairfield ...  # audit only the named slugs (site-wide checks still run)

Exit code 0 = clean, 1 = failures found.
"""
import json
import os
import re
import sys

REPO = "/Users/liampc/Documents/Reggie's/Website"
LOC_DIR = os.path.join(REPO, "locations")
HUB = os.path.join(LOC_DIR, "index.html")
SITEMAP = os.path.join(REPO, "sitemap.xml")
IMG_DIR = os.path.join(REPO, "assets", "img", "locations")

BUSINESS_NAME = "Reggie's Window and Gutter Cleaning"
RETIRED_NAMES = ["Reggie's Window & Gutter Cleaning", "Reggie's Windows & Gutters",
                 "Reggie's Window & Gutters"]

REQUIRED_SECTIONS = [
    ("nav", r'<nav class="vntg-nav"'),
    ("hero", r'<section class="vntg-loc-hero'),
    ("services strip", r'<div class="vntg-loc-services-strip'),
    ("intro", r'<section class="vntg-loc-intro'),
    ("housing mix", r'vntg-loc-suburb-section-label">Built for'),
    ("why locals choose us", r'vntg-loc-suburb-section-label">Why locals choose us'),
    ("testimonials", r'<section class="vntg-loc-testimonials'),
    ("already in your neighbourhood", r'vntg-loc-intro-label">Getting to you'),
    ("faq", r'<section class="vntg-faq vntg-loc-faq-soft'),
    ("cta", r'<section class="vntg-cta-wrapper'),
    ("footer", r'<footer class="vntg-footer"'),
]

failures = []
warnings = []


def fail(page, msg):
    failures.append(f"{page}: {msg}")


def warn(page, msg):
    warnings.append(f"{page}: {msg}")


def suburb_slugs():
    return sorted(
        f[:-5] for f in os.listdir(LOC_DIR)
        if f.endswith(".html") and f != "index.html"
    )


def title_case_from_slug(slug):
    special = {"ascot-vale": "Ascot Vale", "brunswick-east": "Brunswick East",
               "clifton-hill": "Clifton Hill"}
    return special.get(slug, slug.replace("-", " ").title())


def body_word_count(html):
    h = re.sub(r"<nav.*?</nav>", "", html, flags=re.S)
    h = re.sub(r"<footer.*?</footer>", "", h, flags=re.S)
    h = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    h = re.sub(r"<svg.*?</svg>", "", h, flags=re.S)
    h = re.sub(r"<head>.*?</head>", "", h, flags=re.S)
    return len(re.sub(r"<[^>]+>", " ", h).split())


def audit_page(slug):
    path = os.path.join(LOC_DIR, f"{slug}.html")
    html = open(path).read()
    name = title_case_from_slug(slug)
    p = f"{slug}.html"

    # --- Title ---
    m = re.search(r"<title>(.*?)</title>", html)
    if not m:
        fail(p, "no <title>")
    else:
        t = m.group(1)
        if len(t) > 60:
            fail(p, f"title is {len(t)} chars (max 60): {t!r}")
        if name.lower() not in t.lower():
            fail(p, f"title does not contain suburb name: {t!r}")

    # --- Meta description ---
    m = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
    if not m:
        fail(p, "no meta description")
    else:
        d = m.group(1)
        if len(d) > 155:
            fail(p, f"meta description is {len(d)} chars (max 155)")
        if name.lower() not in d.lower():
            warn(p, "meta description does not mention the suburb")

    # --- H1 ---
    m = re.search(r"<h1>(.*?)</h1>", html, re.S)
    if not m:
        fail(p, "no <h1>")
    else:
        h1 = m.group(1)
        if "Gutter, Window" not in h1 or "Solar Cleaning" not in h1:
            fail(p, f"H1 not keyword-forward pattern: {h1[:70]!r}")
        if name.lower() not in re.sub(r"<[^>]+>", "", h1).lower():
            fail(p, "H1 does not contain the suburb name")
        if "<em>" not in h1:
            warn(p, "H1 missing <em> around suburb (brand red highlight)")

    # --- Schema ---
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)
    if not m:
        fail(p, "no JSON-LD schema")
    else:
        try:
            data = json.loads(m.group(1))
            if data.get("name") != BUSINESS_NAME:
                fail(p, f"schema name is {data.get('name')!r}, expected {BUSINESS_NAME!r}")
            if "areaServed" not in data:
                fail(p, "schema missing areaServed")
            if "address" in data:
                fail(p, "schema has an 'address' field — must not (service-area business)")
            if len(data.get("makesOffer", [])) != 3:
                warn(p, "schema makesOffer should list all 3 services")
        except json.JSONDecodeError as e:
            fail(p, f"schema is not valid JSON: {e}")

    # --- Head boilerplate ---
    if 'rel="icon" href="/favicon.ico"' not in html:
        fail(p, "missing favicon block")
    if 'name="theme-color"' not in html:
        fail(p, "missing theme-color meta")
    if 'rel="manifest"' not in html:
        fail(p, "missing web manifest link")

    # --- Nav logo alt ---
    if f'alt="{BUSINESS_NAME}"' not in html:
        fail(p, "nav logo alt does not use the exact business name")

    # --- Retired name variants ---
    for retired in RETIRED_NAMES:
        # allow it inside the footer copyright line only
        occurrences = [mm.start() for mm in re.finditer(re.escape(retired), html)]
        for pos in occurrences:
            context = html[max(0, pos - 120):pos + 60]
            if "All rights reserved" not in context:
                fail(p, f"retired business-name variant used outside footer: {retired!r}")
                break

    # --- Sections ---
    for label, pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, html):
            fail(p, f"missing required section: {label}")

    # --- Service inline links ---
    for svc in ["/gutters", "/solar", "/residential"]:
        if f'href="{svc}" class="vntg-inline-link"' not in html:
            fail(p, f"missing inline service link to {svc}")

    # --- FAQ count ---
    faq = html.count('class="vntg-faq-item"')
    if not (8 <= faq <= 10):
        fail(p, f"FAQ count is {faq} (expected 8-10)")

    # --- Hero ---
    if "vntg-loc-hero-noimg" in html:
        if "photo" not in html.lower().split("<section")[1][:400]:
            warn(p, "gradient placeholder hero with no explanatory comment")
    else:
        m = re.search(r'<img src="(/assets/img/locations/[^"]+)"[^>]*class="vntg-loc-hero-img"', html)
        if not m:
            # could be a remote GHL CDN image (older pages)
            if "vntg-loc-hero-img" not in html:
                fail(p, "hero has neither a photo nor the gradient placeholder class")
        else:
            img_path = os.path.join(REPO, m.group(1).lstrip("/"))
            if not os.path.isfile(img_path):
                fail(p, f"hero image file missing on disk: {m.group(1)}")
        if "vntg-loc-hero-overlay" not in html:
            fail(p, "photo hero missing the overlay div")

    # --- Footer ---
    if "/privacy-policy" not in html:
        fail(p, "footer missing Privacy Policy link")

    # --- Word count ---
    wc = body_word_count(html)
    if wc < 900:
        fail(p, f"body word count {wc} is below 900")

    return html


def main():
    slugs = suburb_slugs()
    target = sys.argv[1:] or slugs
    unknown = [s for s in target if s not in slugs]
    if unknown:
        print(f"Unknown slug(s): {', '.join(unknown)}")
        return 1

    pages = {}
    for slug in slugs:
        pages[slug] = open(os.path.join(LOC_DIR, f"{slug}.html")).read()

    for slug in target:
        audit_page(slug)

    # ---------- Site-wide ----------
    hub = open(HUB).read()
    sitemap = open(SITEMAP).read()

    # Link resolution across ALL pages (incl. hub)
    all_sources = dict(pages)
    all_sources["index.html (hub)"] = hub
    for src, html in all_sources.items():
        for href in set(re.findall(r'href="/locations/([a-z-]+)"', html)):
            if href not in slugs:
                fail(src, f"links to /locations/{href} which does not exist")

    # Bidirectional linking
    links = {s: set(re.findall(r'href="/locations/([a-z-]+)"', h)) - {s}
             for s, h in pages.items()}
    for a, targets in links.items():
        for b in targets:
            if b in links and a not in links[b]:
                fail(f"{a}.html", f"links to {b} but {b}.html does not link back (not bidirectional)")

    # Hub page coverage
    hub_live = set(re.findall(r'href="/locations/([a-z-]+)" class="opt-suburb-pill live"', hub))
    for slug in slugs:
        if slug not in hub_live:
            fail("locations/index.html", f"{slug} missing from hub as a live pill")

    # Sitemap coverage (both directions)
    sm_locs = set(re.findall(r"/locations/([a-z-]+)</loc>", sitemap))
    for slug in slugs:
        if slug not in sm_locs:
            fail("sitemap.xml", f"{slug} missing from sitemap")
    for loc in sm_locs:
        if loc not in slugs:
            fail("sitemap.xml", f"lists /locations/{loc} which does not exist")
    if "/locations</loc>" not in sitemap:
        fail("sitemap.xml", "hub page /locations missing from sitemap")

    # ---------- Report ----------
    print(f"Audited {len(target)} suburb page(s); {len(slugs)} live in total.\n")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
        print()
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print(f"  x {f}")
        print("\nAUDIT FAILED")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
