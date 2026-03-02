# Interface Royale: Reusable UI Template for Top-Grossing F2P Mobile Games

Version: 0.1 (2025-09-04)
Owner: Interface Royale

## Purpose
Create a reusable, genre-agnostic UI/UX template that captures the proven patterns of top-grossing F2P mobile games (e.g., Clash Royale-style hubs), optimizing for monetization (ARPDAU, payer conversion, pay depth) and retention (D1/D7/D30).

## Core Principles ("Secret UI Sauce")
- Navigation clarity: Persistent 4–5 tab bar with central primary CTA. Max depth: 2.
- Visible progress: Session, daily, seasonal tracks with progress bars and timers.
- Appointment loops: Time-gated rewards (claim, open, refresh) driving returns.
- Social gravity: Clan feed, requests/donations, co-op goals, and rivalry.
- Smart scarcity: Limited slots (chests/quests), time-limited offers, rotating shops.
- Red-dot hygiene: Badges only on meaningful actions; always resolvable in 1–2 taps.
- Low-friction economy: Clear dual currency, price framing, and soft caps.
- One-handed ergonomics: Primary actions within thumb zone; readable at a glance.
- Delightful reveals: High-juice reward openings, escalating odds/rarity surfacing.
- LiveOps-first: Events calendar, rotating modes, and season pass as backbone.

## Essential Screens (Template)
1) Home (Lobby)
- Above the fold: Player header (level, avatar, trophies/league), currencies (soft, hard, tickets), season timer.
- Primary CTA: Battle/Play centered. Secondary CTAs: Events, Quests, Clan War.
- Progress widgets: Season Pass track, Daily Goals, Chest/Crate slots.
- LiveOps banner carousel: Events, new features, time-limited modes.
- Notification tray: Consolidated “What’s new” digest.

2) Battle/Play Mode Select
- Modes: Ranked, Casual, Events, Practice. Tile cards with rewards preview.
- Entry cost: Tickets/energy/none; communicates expected rewards and time.
- Match config preview: Deck/Loadout summary, last-used reminder, quick edit.

3) Match HUD (genre-agnostic shell)
- Top: Score/timer/status. Middle: Arena/board/canvas. Bottom: Input (deck/cards/buttons), emotes/chat.
- Spectator/Replay overlay: Share, copy link, report, favorite.

4) Collection & Loadouts
- Collection grid: Filters (rarity, role, power), upgradeable highlight, new badge.
- Item detail: Stats, abilities, synergies, upgrade costs, progression nodes.
- Deck builder: Drag/drop, validation (synergy tips, missing roles), auto-fill.

5) Upgrade & Crafting
- Upgrade panel: Required materials, cost, delta preview, confirm.
- Crafting/synthesis: Recipes, pity/protection, duplicate sinks.

6) Quest & Goals
- Daily/weekly: 3–5 objectives with streak and reroll. BP XP integration.
- Missions: Long-term goals, mastery tracks, achievement milestones.

7) Events & Calendar
- Rotating events: Modifiers, limited decks, collabs. Clear schedule and rewards.
- Event hub: Entry, progress, leaderboards, and shop tab scoped to event.

8) Clan/Social
- Feed: Requests, donations, achievements, clan targets.
- Clan War: Multi-day progress, assignments, rewards timeline.
- Chat/Emotes: Inline share of replays, builds, offers.

9) Shop & Offers
- Lanes: Daily Deals, Bundles, Currency, Cosmetics, Tickets.
- Promo framing: Anchors, best value tags, first purchase bonus, starter path.
- Personalization: Segmented offers by cohort, spend depth, inventory gaps.

10) Season Pass (Free + Premium)
- Track: 30–60 tiers, checkpoints, claims all, late-purchase unlocks retroactively.
- Quests: Seasonal XP, challenges, BP-only missions.
- Perks: Queue reducers, bonus currency, cosmetics, skip tokens.

11) Reward Reveal & Inventory
- Chest/Crate opening: Anticipation phases, skip-speedup, duplicate conversion.
- Inventory: Consumables, cosmetics, keys, tickets, sort by use/rarity.

12) Onboarding & FTUE
- 60–120s to core loop. Companion tips, ghost hands, and deferred depth.
- Starter bundle surfacing, safe clan intro, Day 1 streak setup.

13) Settings & Support
- Account linking, parental controls, notifications, graphics, language.
- Help center, known issues, receipt restore, report/appeal.

## Monetization Surfaces
- Shop lanes, rotating featured bundle, daily deals refresh (20–24h), event shops.
- Season Pass (free/premium), progression skips, booster timers, cosmetics.
- Rewarded ads (opt-in) on speedups, extra rolls, bonus currency.
- Subscriptions (optional): VIP perks, daily drip, ad-free reveals.

## Retention Loops (D0/D1/D7)
- D0: FTUE, first win chest, starter bundle, soft tutorial quests.
- D1: Chest slots, daily goals, BP quests, donation unlock.
- D7: Clan War intro, event cadence, mastery milestones, new mode unlock.

## Cross-genre Adaptability
- Replace “deck” with “loadout/abilities”; “cards” with “units/heroes/gear”.
- Preserve screen shells; swap center canvas and HUD widgets per genre.

## Component Library (Atoms → Organisms)
- Atoms: Buttons (Primary/Secondary/Ghost), Badges, Timers, Progress, Currency chips, Tabs, Toggles, Toasts.
- Molecules: Offer card, Reward tile, Event tile, Collection card, Dialog/Sheet.
- Organisms: Bottom Nav, Header, Mode Select Grid, Deck Builder, Season Track, Shop Lanes, Clan Feed, Reveal Flow.

## Instrumentation & Ops
- Events: economy_spend/earn, session_start, shop_view/offer_click/purchase, quest_claim, chest_open, match_start/end, clan_donate, bp_tier_claim.
- A/B hooks: price points, bundle composition, pass perks, daily goal count, timers.
- Remote config: feature flags, rotations, currency sinks, difficulty.

## Accessibility & Internationalization
- Min 12–14pt body, color contrast >= WCAG AA, haptics on core actions.
- RTL support, flexible string lengths, region-specific price points.

## Risks & Mitigations
- Choice overload → curated lanes, limited depth, strong defaults.
- Pay pressure → cosmetics-first and progression-protected PvP brackets.
- Event fatigue → clear off-weeks, calendar visibility, rewards worth time.

## Deliverables
- Wireframes per screen shell.
- Figma component library mapping to atoms/molecules/organisms.
- JSON schema for navigation and surface composition.

