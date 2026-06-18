# StudyPet Frontend UI Implementation Notes

## Scope

This document records the June 18, 2026 UI redesign for the StudyPet frontend.

The implementation focuses on the feasible parts of the provided design prompts:

- Premium light-mode dashboard with soft studio lighting.
- Central animated pet avatar as the primary screen focus.
- Frosted-glass bottom dock with three module entries.
- AI Pet Chat panel connected to the backend mood/chat API.
- Study Planner left drawer connected to the backend plan API.
- Focus Tracker right overlay with local timer and check-in recording.

No API key or secret is stored in the frontend.

## Files Changed

- `frontend/src/App.vue`
  - Rebuilt the page layout into a dashboard shell.
  - Added the three module surfaces: chat sheet, planner drawer, and focus overlay.
  - Added a local 25-minute countdown timer for the focus module.
  - Preserved the existing Pinia store calls for chat, planning, pet selection, and check-in.

- `frontend/src/styles.css`
  - Replaced the dark prototype styling with a light glassmorphism visual system.
  - Added responsive behavior for desktop and mobile.
  - Added visible focus states and `prefers-reduced-motion` support.

## Architecture

### Central Pet Stage

The desktop pet remains the main interaction anchor. It is rendered by:

```text
App.vue
  -> CompanionSprite.vue
    -> canvas sprite animation from public/assets/companion/*
```

Pet state is controlled by `store.companionAction`:

- `idle`: neutral state
- `comfort`: chat/support state
- `intro`: planning state
- `focus`: study/check-in state
- `happy`: successful check-in or timer completion

Clicking the pet after companion confirmation opens the chat module.

### Bottom Dock

The dock has three fixed module entries:

- `AI Pet Chat`
- `Study Planner`
- `Focus Tracker`

Each button calls `store.openModule(moduleName)`. The active module controls which glass panel is visible.

### Chat Module

UI location:

```text
Right-bottom floating sheet
```

State and API path:

```text
store.runMood()
  -> api.moodCheck()
  -> POST /api/mood/check
```

The module keeps the existing `chatHistory` behavior and sends recent context to the backend.

### Study Planner Module

UI location:

```text
Left slide-in drawer
```

State and API path:

```text
store.runPlan()
  -> api.generatePlan()
  -> POST /api/plan/generate
```

The drawer contains:

- Goal form fields.
- A weekly progress indicator.
- Editable daily task timeline.
- Optional weekly plan summaries when returned by the backend.

The default timeline shown before API generation is local placeholder UI only. Generated API results replace it through `store.planItems`.

### Focus Tracker Module

UI location:

```text
Right-side overlay
```

Behavior:

- 25-minute local countdown timer.
- Start, pause, and reset controls.
- Local subject/minutes check-in through `store.addCheckin()`.
- Displays streak days and today's total study minutes from Pinia state.

This module intentionally does not call the API.

## Design System

### Palette

- Ink: `#172033`
- Muted text: `#687386`
- Frosted surface: `rgba(255, 255, 255, 0.58)`
- Primary blue: `#2563EB`
- Accent lime: `#A3E635`
- Background: light cream to cool grey gradient

### Layout

The app uses a single-screen spatial model:

```text
Top-left brand
Center pet avatar stage
Bottom glass dock
Left planner drawer
Right focus overlay
Right-bottom chat sheet
```

The pet avatar is deliberately not wrapped in a heavy card, so it feels like the live desktop companion rather than a decorative illustration.

### Accessibility and UX Notes

- Interactive controls use native `button`, `input`, and `textarea`.
- Icon-only close buttons have `aria-label`.
- Form fields have visible labels.
- Keyboard focus states are visible.
- Tap targets are generally at least 44px high.
- Motion is reduced under `prefers-reduced-motion: reduce`.
- Timer numbers use tabular figures to avoid layout jitter.

## API Contracts Used

The frontend still depends on:

```text
POST /api/mood/check
POST /api/plan/generate
```

The frontend base URL is read from:

```text
VITE_API_BASE_URL
```

Fallback:

```text
http://localhost:8000/api
```

## Verification

Frontend build command:

```powershell
cd E:\GIT-Projiects\Study-Pet\frontend
npm run build
```

Current result:

```text
Build passed.
```

Known warning:

```text
Some chunks are larger than 500 kB after minification.
```

This is a bundle-size warning, not a functional error. It can be optimized later with code splitting or by reviewing unused dependencies.

## Future Review Checklist

- Confirm pet sprite framing for all five companions on desktop and mobile.
- Test chat with the deployed backend URL in `VITE_API_BASE_URL`.
- Test plan generation with real backend responses containing `plan` and `weekly_plan`.
- Confirm Render backend is using Python 3.12.x.
- Consider splitting frontend chunks if production load time becomes slow.
