# The 200 Club of Hawaii — Website Design Spec

**Date:** 2026-05-10  
**Type:** Static single-file HTML splash page  
**Location in repo:** `200-club/index.html`

---

## Overview

A one-page splash site for The 200 Club of Hawaii — a nonprofit that collects membership dues and donations, and distributes benefit payments to the families of Honolulu Police Department and Honolulu Fire Department officers who die in the line of duty.

---

## Visual Design

- **Color palette:** Deep navy (`#0f1e3d`, `#1a2744`, `#162039`) with gold accents (`#c9a84c`) and light blue-grey text (`#8fa3cc`, `#d0d8e8`)
- **Typography:** Georgia (serif) for headings and body; letter-spaced uppercase labels for section headers
- **Style:** Official and authoritative — reflects the prestige and gravity of HPD and HFD
- **Badges:** HPD and HFD official logos/badges displayed side by side as a trust signal; placeholder images used until official assets are provided

---

## Page Sections (top to bottom)

### 1. Hero
- Club name: **THE 200 CLUB** (large, bold, letter-spaced)
- Sub-label: `HONOLULU, HAWAII`
- Tagline: `HONORING THOSE WHO SERVE`
- Gold bottom border separating from next section

### 2. Partner Badges
- HPD badge (left) and HFD badge (right) displayed side by side with a divider
- Each badge has a department name label beneath it
- HPD badge bordered in gold; HFD badge bordered in red

### 3. Mission Statement
- Section label: `OUR MISSION`
- Placeholder body text describing the club's purpose: providing financial support to families of fallen HPD/HFD officers
- Pull quote: *"When a hero falls, we stand with their family."*
- **TODO:** Replace placeholder text with exact bylaws language when provided

### 4. How It Works
- Section label: `HOW IT WORKS`
- Three numbered steps (gold circle numbers):
  1. Members and donors contribute annual dues or one-time donations
  2. Funds are pooled and held in reserve for families in need
  3. When an officer or firefighter falls in the line of duty, the family receives a benefit payment

### 5. Zeffy Donation / Dues Form
- Section label: `SUPPORT THE MISSION`
- Heading: *Become a Member or Donate*
- Supporting copy noting 0% platform fees via Zeffy
- **Embedded Zeffy iframe** for the donation/dues form (preset amounts: $25, $50, $100, custom)
- **TODO:** Replace iframe `src` with actual Zeffy embed URL once account is created at zeffy.com
- Note: Zeffy requires a free nonprofit account setup before the embed URL is available

### 6. Footer
- Copyright line: `© 2025 THE 200 CLUB OF HAWAII · ALL RIGHTS RESERVED`

---

## Technical Spec

| Attribute | Value |
|---|---|
| Build type | Static HTML — single file, no build step |
| File | `200-club/index.html` — all HTML, CSS, JS inline |
| Hosting | Any static host (GitHub Pages, Netlify, etc.) |
| Dependencies | None — no frameworks, no npm |
| Payment | Zeffy embedded iframe (0% platform fees for nonprofits) |
| Badges | `<img>` tags pointing to publicly available HPD/HFD badge URLs |

---

## Open Items (before launch)

1. **Bylaws mission text** — swap placeholder copy with the exact language from the club bylaws
2. **Zeffy account** — create a free nonprofit account at zeffy.com, set up a donation/membership form, and get the embed iframe URL
3. **Official badge images** — replace placeholder badge images with official HPD and HFD logos once available
4. **Dues amount** — confirm the annual membership dues amount to pre-fill in the Zeffy form

---

## Out of Scope

- Multi-page navigation
- Member login or portal
- Event calendar
- CMS or admin interface
