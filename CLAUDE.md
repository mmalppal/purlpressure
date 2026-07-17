# purlpressure.com — Project Context for Claude

## What this is

The marketing + content home for **Purl Pressure** — Mallory Iversen's knitting brand. Hub for:

- **Weekly Obsessions** blog (MDX)
- **Other Posts** blog (MDX) — same format as Weekly Obsessions, for posts that don't fit the weekly cadence
- **Palette Pairings** series (placeholder for now)
- **Plied** placeholder (future product)
- **About** page

Not a SaaS. Not behind auth. Static marketing + blog.

## Stack

- **Astro 5** (static output) + MDX content collections
- **Vercel** adapter — `output: 'static'`, `adapter: vercel()`
- **No UI framework** — raw CSS with design tokens in `src/styles/global.css`
- **Fonts**: Luckybones (display, self-hosted TTF), Stylish (body, Google Fonts), Now (labels/mono, self-hosted TTF) — see `public/fonts/` and `Base.astro`

## Aesthetic

Warm textile-studio palette (terracotta, clary sage, periwinkle, walnut, oxblood-pink), pushed weirder:

- Heavy bold italic Luckybones as display font (clamp up to ~220px) — self-hosted, very distinctive
- Off-grid layout (rotated cards, overlapping color blocks, asymmetric grids)
- Risograph noise overlay on body (SVG turbulence, mix-blend-mode: overlay)
- Squiggle SVG dividers (looks like garter stitch)
- Sticker-style rotated pill labels
- Marquee ticker between sections
- Hero is a 3-slab asymmetric grid (terracotta-tint dark / clary sage / periwinkle)
- Buttons "nudge" up on hover with hard offset shadow
- Dark candlelit bg `#1A1410`, never pure black
- All effects honor `prefers-reduced-motion`

## File map

```
astro.config.mjs           — Astro + MDX + Vercel adapter
src/
  content/
    config.ts              — Zod schema shared by `obsessions` + `other-posts` collections
    obsessions/*.mdx       — Weekly Obsessions posts
    other-posts/*.mdx      — Other Posts (same frontmatter shape as obsessions)
  styles/global.css        — All tokens + global styles + prose + utilities
  layouts/Base.astro       — HTML shell, nav, footer, fonts, meta/OG
  components/
    Nav.astro              — Sticky scroll nav
    Footer.astro           — Three-col footer
    PostCard.astro         — WO post card (color block + body, alt-tilted)
    AppCard.astro          — Tool/app card (future products)
    StickerLabel.astro     — Rotated pill label
    SquiggleDivider.astro  — Garter-stitch-y SVG divider
    Marquee.astro          — Auto-scrolling ticker
  pages/
    index.astro                          — Homepage (3-slab hero + apps + latest 3 WO)
    about.astro                          — About Mallory
    weekly-obsessions/index.astro        — Archive grid
    weekly-obsessions/[slug].astro       — Individual post (color band header + sidebar)
    other-posts/index.astro              — Other Posts archive grid (periwinkle-accented)
    other-posts/[slug].astro             — Individual Other Post (mirrors weekly-obsessions)
    palette-pairings/index.astro         — Placeholder + season swatch preview
```

## Adding a Weekly Obsessions post

1. Duplicate any `.mdx` in `src/content/obsessions/`
2. Update frontmatter:
   - `title`, `date`, `excerpt` — required
   - `color`, `accent` — hex for the post's color band; pick from the design tokens
   - `patterns[]` — `{ name, designer, ravelry?, image? }` — shown in the post as image+specs rows
   - `instagramPost` — optional URL to the carousel
3. Write body in MDX. The `.pp-prose` styles render headings, blockquotes, links with terracotta highlight.
4. Push to `main`. Vercel auto-deploys.

Adding an **Other Posts** post works the same way: `.mdx` in `src/content/other-posts/`,
images in `public/other-posts/<slug>/` (`1.jpg` = cover, `2.jpg`+ = pattern slides, ~85%-quality
JPEGs around 250–350KB each).

## Sample posts to replace

The three posts in `src/content/obsessions/` are scaffolding placeholders. Replace with real content — frontmatter + body — but keep at least one post or the homepage's "latest 3" section will show an empty state.

## Design tokens (the short list)

Defined in `src/styles/global.css` as CSS custom properties:

- Backgrounds: `--pp-bg`, `--pp-bg-elevated`, `--pp-bg-sunken`, `--pp-paper`
- Anchors: `--pp-cordovan`, `--pp-merlot`, `--pp-terracotta`, `--pp-walnut`, `--pp-moss`, `--pp-clary-sage`
- Pinks: `--pp-rose`, `--pp-dusty-pink`, `--pp-blush`, `--pp-oxblood-pink`
- Cool: `--pp-periwinkle`, `--pp-shadow-blue`, `--pp-cadet`, `--pp-butter`, `--pp-honey`
- Text: `--pp-text`, `--pp-text-soft`, `--pp-text-muted`, `--pp-text-ghost`
- Spacing: `--pp-1` … `--pp-24` (4px steps)

When adding a new section, prefer existing tokens over new hex values.

## Local dev

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # static build → ./dist
npm run preview      # preview the build
```

## Deployment

- Connected to Vercel project (manual setup required)
- DNS for `purlpressure.com` points at Vercel
- Push to `main` → auto-deploy

## What this isn't

- Not a CMS — content lives in the repo as MDX
- Not multi-author — Mallory writes everything
- Not authenticated — static site, no Supabase, no Stripe
