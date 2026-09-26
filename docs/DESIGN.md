# Lights-out — Design system

Instructions for the coding agent that builds the browser UI. Use only the values in this file. If
something is not covered here, reuse the closest existing token or component; do not invent new
colours, sizes or components.

## Context

- **Project**: the service built by the Lights-out factory for the `tablekeeper` track: diners search
  a restaurant's availability, book a table (single or combined), get a confirmation and look a
  booking up by reference.
- **Audience**: hackathon judges, who score the UI as "coherent, presentation-ready, responsive and
  clear in the states the stage-2 spec identifies". The stage-2 spec asks for "a warm, confident
  hospitality character". The spec is the authority; this file only fixes the visual system.
- **Sources**:
  - Base, precise dark product UI: a four-step surface ladder, 1px hairline borders instead of
    shadows, 4px spacing base, 8px controls and 12px cards, negative tracking on display type, one
    scarce accent.
  - Secondary, developer-terminal look (two traits only): monospace for every identifier, time and
    count, with uppercase tracked eyebrows; and one terminal-style typed line.
- **Originality changes**:
  - Warm-tinted neutrals (brown-black, not blue-black).
  - A single **amber pilot-light accent** instead of the sources' lavender or green: a light left on
    in a dark factory, warm enough for hospitality.
  - Open fonts only.

## Stack

- The factory chooses the service stack. This system is framework-agnostic: **plain CSS custom
  properties** in one stylesheet (`static/tokens.css`) loaded by every screen.
- **No network at runtime.** The container is judged on an internal network with no outbound
  access, and so is the browser. No CDN, no Google Fonts `<link>`, no remote icons.
  - Fonts are vendored into the image at build time as `woff2` and declared with `@font-face`
    (for Node: `@fontsource/inter`, `@fontsource/jetbrains-mono`; otherwise download the `woff2`
    files in the `Dockerfile`).
  - The fallback stacks below must render acceptably if a font file is missing.
- If the factory uses Tailwind, map the tokens instead of hardcoding values:

```js
// tailwind.config.js (only if Tailwind is used)
theme: { extend: {
  colors: { bg:'var(--bg)', 'surface-1':'var(--surface-1)', 'surface-2':'var(--surface-2)',
    'surface-3':'var(--surface-3)', border:'var(--border)', 'border-strong':'var(--border-strong)',
    fg:'var(--fg)', 'fg-muted':'var(--fg-muted)', 'fg-subtle':'var(--fg-subtle)', accent:'var(--accent)',
    'accent-hover':'var(--accent-hover)', 'on-accent':'var(--on-accent)', ring:'var(--ring)',
    success:'var(--success)', danger:'var(--danger)', pending:'var(--pending)' },
  fontFamily: { sans:'var(--font-sans)', mono:'var(--font-mono)' },
  borderRadius: { sm:'var(--radius-sm)', md:'var(--radius-md)', lg:'var(--radius-lg)', xl:'var(--radius-xl)', pill:'var(--radius-pill)' },
}}
```

## Tokens

Dark is the default. Light is a full theme, not an afterthought. The theme is set with
`data-theme` on `<html>`. The initial value comes from a saved choice, else from
`prefers-color-scheme`. Every theme block declares `color-scheme`.

```css
:root {
  color-scheme: dark;
  --bg: #0d0c0b;
  --surface-1: #151412;
  --surface-2: #1c1a18;
  --surface-3: #24221f;
  --border: #2e2b27;
  --border-strong: #756d62;
  --fg: #f5f2ee;
  --fg-muted: #c9c3bb;
  --fg-subtle: #9a938a;
  --accent: #f2a33a;
  --accent-hover: #f7b85e;
  --on-accent: #1a1206;
  --ring: #f2a33a;
  --success: #4cc38a;
  --danger: #f07167;
  --pending: #9db4ff;
  --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-pill: 9999px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-24: 96px;
  --shadow-overlay: 0 20px 60px rgb(0 0 0 / 0.55), 0 0 0 1px var(--border);
  --glow-accent: 0 0 0 1px var(--accent), 0 0 18px rgb(242 163 58 / 0.28);
}
[data-theme="light"] {
  color-scheme: light;
  --bg: #faf8f5;
  --surface-1: #ffffff;
  --surface-2: #f3f0eb;
  --surface-3: #ebe7e0;
  --border: #e2ddd5;
  --border-strong: #9c9488;
  --fg: #1b1916;
  --fg-muted: #4a453f;
  --fg-subtle: #6b645b;
  --accent: #a4560b;
  --accent-hover: #8a4708;
  --on-accent: #ffffff;
  --ring: #a4560b;
  --success: #1c7547;
  --danger: #b3261e;
  --pending: #3552b8;
  --shadow-overlay: 0 20px 60px rgb(27 25 22 / 0.18), 0 0 0 1px var(--border);
  --glow-accent: 0 0 0 1px var(--accent), 0 0 14px rgb(164 86 11 / 0.22);
}
```

Measured contrast (WCAG): every text token is ≥ 5.1:1 on `--bg`, `--surface-1` and `--surface-2`
in both themes. `--on-accent` on `--accent` is 8.9:1 dark and 5.4:1 light. `--border-strong` on
`--surface-1` is 3.6:1 dark and 3.0:1 light, which covers input and control boundaries.
`--border` is decorative only and never the sole boundary of a control.

## Typography

- Two families only: `--font-sans` (Inter 400/500/600) for prose and UI, `--font-mono`
  (JetBrains Mono 400/500) for anything a machine produced. That covers booking references,
  times, dates in grids, party sizes, table labels in receipts, counts and status codes.
- Scale (rem at 16px root):

| Role | Size | Weight | Line height | Tracking |
|---|---|---|---|---|
| display | 2.5rem (1.75rem < 480px) | 600 | 1.1 | -0.025em |
| title | 1.75rem | 600 | 1.2 | -0.02em |
| heading | 1.25rem | 600 | 1.3 | -0.01em |
| body-lg | 1.125rem | 400 | 1.5 | 0 |
| body | 1rem | 400 | 1.5 | 0 |
| body-sm | 0.875rem | 400 | 1.5 | 0 |
| caption | 0.75rem | 500 | 1.4 | 0 |
| eyebrow | 0.75rem | 600, uppercase | 1.4 | 0.16em |
| mono | 0.875rem | 400 | 1.5 | 0 |

- Use `font-variant-numeric: tabular-nums` on every number that sits in a column or updates.
- Display never goes above weight 600.

## Spacing, grid, radii and shadows

- Spacing: only `--space-*` (4px base). Card padding `--space-6`; section gap `--space-12`
  (`--space-24` between page bands on desktop); control padding `--space-2` × `--space-4`.
- Layout: max content width 1120px, side gutter `--space-4` on mobile and `--space-8` on desktop.
  Single column below 768px.
- **No horizontal page scroll at 375px**:
  - Grids wrap.
  - Long names wrap (`overflow-wrap: anywhere`) and are never clipped.
  - Tables become stacked rows.
- Radii:
  - `--radius-md` for buttons, inputs and slots.
  - `--radius-lg` for cards.
  - `--radius-xl` for the main panel.
  - `--radius-pill` only for status badges.
- Depth is the surface ladder plus a 1px border. Page = `--bg`; card = `--surface-1` plus
  `--border`; hovered or selected = `--surface-2`; menu or popover = `--surface-3` plus
  `--shadow-overlay`.
  - No drop shadows on cards.
  - `--glow-accent` only on the selected slot and the focused primary action.

## Components

Every interactive element has hover, focus-visible, disabled and, where it acts, loading and error
states. Focus is always `outline: 2px solid var(--ring); outline-offset: 2px`, never removed.

- **Button, primary**: `--accent` fill, `--on-accent` text, 500 weight, `--radius-md`, min height
  44px.
  - Hover: `--accent-hover`.
  - Disabled: 45% opacity and `cursor: not-allowed`.
  - Loading: label stays, an inline 14px spinner is added and `aria-busy="true"` is set; double
    submit is prevented.
  - One primary per view.
- **Button, secondary**: `--surface-1` fill, `--fg` text, 1px `--border-strong`; hover
  `--surface-2`.
- **Button, ghost**: no fill, `--fg-muted` text; hover `--fg`.
- **Input / select**: `--surface-1`, 1px `--border-strong`, `--radius-md`, min height 44px, and a
  **visible label above** (body-sm, `--fg-muted`).
  - Error: `--danger` border plus a message below, linked with `aria-describedby`.
  - Disabled: `--surface-2` with `--fg-subtle`.
- **Card**: `--surface-1`, 1px `--border`, `--radius-lg`, `--space-6` padding. Card title
  `heading`; eyebrow above in `eyebrow` `--fg-subtle`.
- **Availability slot** (the key component). A button in a wrapping grid; the time is in mono,
  the seating label in sans. Each state must differ by more than colour:

| State | Look |
|---|---|
| available | `--surface-2`, `--fg`, 1px `--border-strong` |
| unavailable | `--bg`, `--fg-subtle`, dashed `--border`, time struck through, `aria-disabled="true"` |
| selected | `--accent` fill, `--on-accent` text, `--glow-accent`, check icon |
| loading | skeleton: `--surface-2` block with a slow opacity pulse, no text |

- **Combined seating option**: rendered as one option with a human label ("Window 4 + Window 5 ·
  seats 6"), with a small "combined" badge. Never a joined technical id.
- **Outcome banner**: full width, icon plus title plus one line, `--radius-lg`, 1px border in the
  state colour, `--surface-1` fill.
  - successful: `--success`
  - refused: `--danger`, with the reason in plain words
  - uncertain: `--pending`, dashed border, "We couldn't confirm yet — checking…"
- **Status badge**: pill, caption, 1px border in the state colour, text in the state colour.
- **Receipt**: a card with the booking reference in mono at `title` size, followed by
  restaurant, date, time, party and tables as a two-column definition list (stacked below 480px).
- **Top nav**: `--bg`, 56px, 1px `--border` bottom. Wordmark on the left; links (Search, Look up)
  and the signed-in user's display name on the right. Identical on every route; collapses to a
  menu button below 480px.
- **Empty / loading / error states**: a centered card with one sentence and one action. Loading
  uses skeletons shaped like the final content, never a lone spinner on a blank page.

## Screens

| Route | Structure | Components |
|---|---|---|
| `/` | Nav → search bar (restaurant, date, party size, primary "Search") → availability grid grouped by time → selected slot opens the booking form below (not a new page) | nav, input/select, button, availability slot, combined seating option, skeletons, empty state |
| booking form | Card with contact fields and the chosen slot summary; stays on screen after success | input, button primary (loading state), outcome banner |
| confirmation | Outcome banner plus receipt; the reference is typed in (effect 2) | outcome banner, receipt, status badge |
| `/lookup` | Nav → one input for the reference plus "Look up" → receipt or error state | input, button, receipt, empty and error states |
| `/signup`, `/login` | Centered card, max 400px, labelled inputs, primary action, link to the other screen | card, input, button |

## Effects

Two effects only; everything else is instant or a 150ms colour transition.

1. **Lights on (availability grid)**:
   - Animation: when results arrive, slots fade in from 0 to 1 opacity and 4px lower to 0, in
     reading order, with a 20ms stagger capped at 300ms total. Only once per result set; never on
     re-render of the same data.
   - Reduced motion: slots appear in their final state at once.
2. **Typed reference (confirmation and lookup)**:
   - Animation: the booking reference types in character by character in `--font-mono`, 35ms per
     character, with an amber block cursor that blinks twice and disappears. The full reference is
     in the DOM from the start (screen readers and copy get the real value); only its visible
     width animates.
   - Reduced motion: the reference is shown complete, with no cursor.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

## Rules

- **Do**:
  - Use tokens for every colour, radius and space.
  - Show human-readable restaurant and table names first and put ids in mono.
  - Keep one primary action per view.
  - Make every state readable without colour (icon, text or border style).
  - Keep navigation identical across routes.
- **Don't**:
  - Load anything from the network at runtime.
  - Add a second accent colour.
  - Use the accent as a large background.
  - Put shadows on cards, use pill-shaped buttons or set display weights above 600.
  - Remove focus outlines.
  - Clip or ellipsize names that the diner needs.
  - Show raw JSON or API error codes to the diner.
- Theme toggle in the nav (sun/moon icon button, `aria-label` "Switch to light/dark theme"). The
  choice is saved in `localStorage` inside `try/catch`, and the page must work if storage throws.
- The spec wins over this file on any behaviour, label or element requirement.

## Verification checklist

- [ ] Both themes: every screen checked in dark and light; text ≥ 4.5:1, large text and control
      boundaries ≥ 3:1, measured per theme.
- [ ] 375px and 1280px: no horizontal page scroll; a 60-character restaurant name with no spaces
      wraps without overflow.
- [ ] Keyboard only: every flow completes with Tab, Enter and Space; focus ring visible on every
      control.
- [ ] Available, unavailable, selected, loading, successful, refused and uncertain are
      distinguishable in grayscale.
- [ ] `prefers-reduced-motion: reduce`: both effects show their final state with no animation.
- [ ] Offline container (`--network none`): fonts render (vendored) and no request leaves the
      page.
- [ ] Empty, loading and error states exist on `/` and `/lookup`.
