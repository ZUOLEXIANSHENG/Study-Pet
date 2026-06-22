# StudyPet Concept Mockups

This folder stores visual references for the next StudyPet frontend iteration.

## Files

- `studypet-home-image2.png`
  - Generated through the user-provided Image2-compatible API.
  - Target page: Home dashboard.
  - Focus: central pet, top bar, pet speech/info, AI chat, study plan, overview, calendar.

- `studypet-planning-concept.png`
  - Generated with the built-in image generation fallback after the Image2 upstream service failed.
  - Target page: Study Planning.
  - Focus: weekly roadmap timeline, draggable task cards, right AI planner panel.

- `studypet-checkin-concept.png`
  - Generated with the built-in image generation fallback after the Image2 upstream service failed.
  - Target page: Study Check-in.
  - Focus: streak, large check-in CTA, pet celebration, EXP feedback, heatmap calendar.

- `studypet-growth-concept.png`
  - Generated with the built-in image generation fallback after the Image2 upstream service failed.
  - Target page: Pet Growth Center.
  - Focus: central pet growth, achievements, unlocked abilities, milestone timeline.

## Image2 Status

The Image2 endpoint worked once for the home dashboard, then later returned upstream errors:

- `Upstream request failed`
- `Upstream service temporarily unavailable`

The request format and API key were already validated by the successful home image generation. The later failures appear to be provider-side availability issues.

## Design Direction

The target UI style remains:

- Apple Human Interface Design x Notion x Arc Browser
- calm, warm, intelligent, minimal, premium
- emotionally engaging, but not childish
- pet as the emotional center of the product
- primary color `#6366F1`
- secondary color `#A5B4FC`
- background `#F8FAFC`
- white glassmorphism cards with soft shadows
