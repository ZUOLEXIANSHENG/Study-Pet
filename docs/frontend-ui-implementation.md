# StudyPet Frontend UI Implementation Notes

## Scope

This document records the current premium StudyPet frontend design.

The interface now follows the requested product direction:

- Apple Human Interface Design
- Notion-like calm spacing
- Arc-inspired light shell and tabs
- Duolingo-style emotional reinforcement
- modern SaaS clarity without enterprise heaviness

The experience is organized as four desktop pages:

1. Home
2. Planning
3. Check-in
4. Growth

## Files Changed

- `frontend/src/App.vue`
  - Replaced the old avatar-selection flow with a page-based desktop shell.
  - Added the four-page navigation model.
  - Added top bar, hero stage, bottom cards, planning page, check-in page, and growth page.
  - Wired StudyPet interactions to the existing Pinia store for chat, planning, and check-in.

- `frontend/src/components/StudyPetAvatar.vue`
  - New original StudyPet companion built in SVG/CSS.
  - Includes breathing, floating particles, ambient aura, and reward labels.
  - This replaces the earlier 3D/anime sprite approach for the current concept implementation.

- `frontend/src/styles.css`
  - New light glassmorphism system.
  - Premium surface hierarchy, soft shadows, large whitespace, and responsive behavior.
  - Animation support for breathing, floating rewards, celebration, and micro-interactions.

## Architecture

### Home Page

The home page uses a three-zone structure:

```text
Top bar
Hero area
Bottom functional cards
```

Hero composition:

- Left: speech bubble + pet information card
- Center: large StudyPet avatar on a floating platform
- Right: AI chat panel

Bottom functional cards:

- Today’s Study Plan
- Today’s Learning Overview
- Study Calendar

### Planning Page

The planning page uses:

- Left sidebar for roadmap context
- Center weekly timeline
- Right AI planning assistant form

The center timeline is intentionally card-based and wide, with seven day columns to support a calm roadmap feel.

### Check-in Page

The check-in page uses:

- Top streak hero
- Center check-in call-to-action with celebration effect
- Bottom statistics row
- Right study calendar heatmap

The check-in action uses local state and the existing store check-in behavior.

### Growth Page

The growth page uses:

- Left achievements panel
- Center evolution stage with the StudyPet avatar
- Right unlocked abilities panel
- Bottom growth timeline

This page is designed to feel emotional and companion-like rather than analytical.

## Companion Asset Strategy

The current implementation uses a custom SVG/CSS companion instead of the old imported sprite characters.

Why this choice was made:

- It guarantees a stable premium look without depending on external art assets.
- It fits the current objective of a concept-first, controllable front-end.
- It is easy to replace later with generated bitmap art or a manually designed illustration.

If you later want to swap in generated image art:

- Replace `frontend/src/components/StudyPetAvatar.vue`
- Keep the page layout and card system unchanged
- Preserve the hero platform, aura, and reward layers around the new asset

Recommended replacement path:

- Render or generate a single centered companion asset.
- Match the current pastel blue/purple palette.
- Keep the silhouette simple enough to work in the hero shell.

## State and Data Flow

The frontend still uses the existing store for conversational and planning actions.

### Chat

```text
store.runMood()
  -> api.moodCheck()
  -> POST /api/mood/check
```

### Study Plan

```text
store.runPlan()
  -> api.generatePlan()
  -> POST /api/plan/generate
```

### Check-in

```text
store.addCheckin()
  -> local state update
```

## Design System

### Palette

- Primary: `#6366F1`
- Secondary: `#A5B4FC`
- Background: `#F8FAFC`
- Ink: `#111827`
- Muted: `#64748B`
- Surface: translucent white glass

### Layout

The main home page is tuned for a 1440px desktop shell with:

- top navigation bar
- center hero area
- bottom functional area

The pet is visually dominant and takes most of the attention in the composition.

### Typography

The design uses a clean sans stack with no decorative face.

Principles:

- readable
- restrained
- low contrast only where intentional
- no playful novelty type

## Accessibility and UX Notes

- Buttons and inputs remain native elements.
- Reduced motion is respected.
- Focus rings are visible.
- Layout collapses to a single column on smaller widths.
- Celebration effects are non-blocking and purely decorative.

## Verification

Current verification:

```powershell
cd E:\GIT-Projiects\Study-Pet\frontend
npm run build
```

Result:

- Build passed successfully.

Known warning:

- Vite reports a bundle-size warning due to existing dependencies.

## Future Work

- Replace the SVG companion with a generated bitmap or externally designed avatar if you decide to use image generation later.
- Split the large frontend bundle if production load time becomes an issue.
- Connect more of the growth page to real backend reports when ready.
