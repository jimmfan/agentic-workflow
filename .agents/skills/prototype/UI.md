# UI Prototype

Generate **several radically different UI variations** on a single route, switchable from a floating bottom bar.
The user flips between variants in the browser, picks one (or steals bits from each), then throws the rest away.

If the question is about logic/state rather than what something looks like — wrong branch.
Use [LOGIC.md](LOGIC.md).

## When this is the right shape

- "What should this page look like?"
- "I want to see a few options for this dashboard before committing."
- "Try a different layout for the settings screen."
- Any time the user would otherwise spend a day picking between three vague mockups in their head.

## Choose the host page

Use an existing page when the prototype fits there, including a new section, card, or step within that page.
Real surrounding content makes layout and density easier to judge.
Create a temporary route only when no existing page is a suitable host.

### Sub-shape A — adjustment to an existing page (preferred)

Variants are rendered **on the same route**, gated by a `?variant=` URL search param.
Preserve existing params and auth, use only authorized read-only data fetching, and stub actions that would mutate real data.
Gate prototype variants to the development preview so production rendering stays intact.

### Sub-shape B — a new page (last resort)

Create a **throwaway route** following whatever routing convention the project already uses — don't invent a new top-level structure.
Name it so it's obviously a prototype (e.g. include the word `prototype` in the path or filename).
Same `?variant=` pattern.

In both sub-shapes the floating bottom bar is identical.

## Process

### 1. State the question and pick N

Default to **3 variants**.
More than 5 stops being radically different and starts being noise — cap there.

Write down the plan in one line, in the prototype's location or a top-of-file comment:

> "Three variants of the settings page, switchable via `?variant=`, on the existing `/settings` route."

### 2. Generate radically different variants

Draft each variant.
Hold each one to:

- The page's purpose and the data it has access to.
- The project's component library / styling system (TailwindCSS, shadcn, MUI, plain CSS, whatever).
- A clear exported component name, e.g. `VariantA`, `VariantB`, `VariantC`.

Variants must be **structurally different** — different layout, different information hierarchy, different primary affordance, not just different colours.
If two drafts come out too similar, redo one with explicit "do not use a card grid" guidance.

### 3. Wire them together

Create a single switcher component on the route:

```tsx
// Inside the development-only preview — adapt to the project's framework
const variant = searchParams.get('variant') ?? 'A';
return (
  <>
    {variant === 'A' && <VariantA {...data} />}
    {variant === 'B' && <VariantB {...data} />}
    {variant === 'C' && <VariantC {...data} />}
    <PrototypeSwitcher variants={['A','B','C']} current={variant} />
  </>
);
```

For sub-shape A (existing page): keep authorized read-only data fetching above the switcher; only the preview's rendered subtree changes per variant.

For sub-shape B (new page): the throwaway route under `/prototype/<name>` mounts the same switcher.

### 4. Build the floating switcher

A small fixed-position bar at the bottom-centre of the screen with three pieces:

- **Left arrow** — cycles to the previous variant (wraps around).
- **Variant label** — shows the current variant key and, if the variant exports a name, that name too.
  e.g. `B — Sidebar layout`.
- **Right arrow** — cycles forward (wraps around).

Behaviour:

- Clicking an arrow updates the URL search param (use the framework's router — `router.replace` on Next, `navigate` on React Router, etc) so the variant is shareable and reload-stable.
- Keyboard: `←` and `→` arrow keys also cycle.
  Don't intercept arrow keys when an `<input>`, `<textarea>`, or `[contenteditable]` is focused.
- Visually distinct from the page (e.g. high-contrast pill, subtle shadow) so it's obviously not part of the design being evaluated.
- Hidden in production builds — gate on `process.env.NODE_ENV !== 'production'` or an equivalent check, so a stray prototype merge can't ship the bar to users.

Put the switcher in a single shared component so both sub-shapes can reuse it.
Locate it wherever shared UI lives in the project.

### 5. Hand it over

Surface the URL and `?variant=` keys so the user can compare variants and combine useful elements.

### 6. Capture the answer and clean up

Once a variant has won, capture the answer — which variant and why — then capture the prototype the way the [SKILL](SKILL.md) describes.
When production adoption is authorized, implement and verify the accepted design to production standards:

- **Sub-shape A** — fold the winner into the existing page; drop the losing variants and the switcher from main.
- **Sub-shape B** — promote the winning variant to a real route; drop the throwaway route and the switcher from main.

When preservation is authorized, keep the full set of variants as the primary source on the throwaway branch with a usable reference.
Any commits or publication require authorization for those actions when performed.
Apply the same authorization boundary to removing prototype files; do not discard unrelated work.

## Keep variants independent

- **Sharing too much code between variants.**
  A shared `<Header>` is fine; a shared `<Layout>` defeats the point.
  Each variant should be free to throw out the layout.
