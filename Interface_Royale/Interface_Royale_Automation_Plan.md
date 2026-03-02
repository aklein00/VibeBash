# Interface Royale Automation Plan: From Idea → Design Doc → Stub Assets

Version: 0.1 (2025-09-04)
Owner: Interface Royale

## Goal
Automate the pipeline to: (1) accept a short game idea, (2) generate a reviewable design document, and (3) output a comprehensive asset list plus stub assets aligned to the Interface Royale template.

## Inputs
- Idea form (JSON): title, theme, genre, target audience, session length, monetization preference, PvP/PvE, social strength, visual style notes.
- Template knobs (JSON): number of tabs, presence of clan, battle pass on/off, event cadence, economy structure (soft/hard/keys/tickets).

## Outputs
- Design doc (Markdown): tailored screens, loops, economy, LiveOps plan, monetization.
- Asset list (CSV): UI, UX flows, VFX/SFX, localization strings, with specs.
- Stub assets: vector PNG/SVG/JSON metadata, placeholder audio, sample animation JSON.

## System Architecture
- Orchestrator: CLI or small web app (Node/Python) that reads idea.json and template.json.
- Generators
  - Screen Blueprint Generator: maps template screens to the chosen genre and produces Markdown sections + wireframe JSON.
  - Economy & Loop Generator: builds D0/D1/D7 loops and economy sinks/sources based on knobs.
  - Monetization Planner: composes shop lanes, bundles, pass perks, events cadence.
  - Asset Compiler: enumerates assets per screen blueprint and economy/monetization plan, emits CSV.
  - Stub Asset Fabricator: creates PNG/SVG placeholders, atlas JSON, and silent/bleep SFX.
- Artifact Store: writes to project folder with date-stamped subdir.

## Data Schemas
- idea.json
```
{
  "title": "",
  "theme": "",
  "genre": "idle_clicker|deck_battler|auto_chess|runner|puzzle",
  "targetAudience": "",
  "sessionMinutes": 3,
  "social": "none|light|strong",
  "pvp": false,
  "monetization": "bp_shop_ads|cosmetics_only|subs_bp",
  "styleNotes": ""
}
```
- template.json
```
{
  "tabs": ["Home","Play","Collection","Shop","Clan"],
  "hasBattlePass": true,
  "hasClan": true,
  "dailyDeals": 6,
  "eventCadenceDays": 7,
  "currencies": ["gold","gems","tickets"],
  "timeGates": {"chestSlots": 4, "questSlots": 3}
}
```

## Generation Steps
1. Parse inputs; validate enums and ranges.
2. Select screen shells: Home, Play, Collection, Events, Shop, Clan, Pass, Rewards, Settings.
3. Specialize copy and flows based on genre: rename deck→loadout; cards→upgrades for idle.
4. Synthesize loops: FTUE goals, D1 streak, D7 milestones, timers.
5. Monetization: choose price points, bundle sizes, deal rotations, pass perks.
6. Emit design doc sections (Markdown) and a machine-readable wireframe.json.
7. Compile asset inventory with specs and usage context; write assets.csv.
8. Render stub assets: 
   - UI: 9-slice buttons, tabs, badges in light/dark variants.
   - Icons: currencies, roles, rarity, timers, notifications.
   - VFX: simple particle JSON; SFX: click, claim, open.
   - Layout previews as 1242x2688 PNGs.

## File Outputs
- /Interface_Royale/outputs/{date}/
  - {title}_Design.md
  - {title}_Wireframes.json
  - {title}_Assets.csv
  - stubs/ui/*.png, *.svg
  - stubs/audio/*.wav

## Review & Iteration
- Lint: schema validate JSON; check missing specs in CSV.
- Diff-friendly: stable ordering of lists.
- Stakeholder checklist: monetization surfaces, loops, screens, accessibility, localization.

## Roadmap
- v0.1: CLI with deterministic templates.
- v0.2: Add segmentation-aware bundles and price testing matrix.
- v0.3: Figma plugin to sync components and export stubs.

