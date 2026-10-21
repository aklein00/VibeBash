# F2P UX Workflow Template — Royal Scibbles

A reusable, grayscale UX kit for free-to-play mobile games. It contains **106 mobile screen states, 663 labeled control routes, 38 system branches, and 21 detailed flow sheets**. Royal Scibbles uses Clash Royale as its primary design reference: an eight-card deck, four-card battle hand, regenerating elixir, collection upgrades, and chest progression. Gold, Gems, gameplay tickets, FTUE, live ops, purchases, and recovery are connected through explicit screen destinations.

The kit is a design and navigation prototype. It is not a playable game, production economy, backend, or payment integration. All prices, timers, rewards, balances, and thresholds are configurable examples.

## Start here

1. Clone/download this repository and open [`preview.html`](preview.html) in a browser. GitHub's file viewer displays the HTML source; run the downloaded file to use it.
2. Choose **Start FTUE** to experience the first session, or use the left navigation to jump to a screen.
3. Click the numbered controls inside a phone. The panel beside it explains the destination and state rule.
4. Use **Simulate system outcome** outside the phone for match results, elapsed timers, receipt verification, and connection failures.
5. Choose **View flow sheets** to see multiple complete wireframes, button destinations, and decision branches together.

You can also serve it locally from the repository root:

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory F2P_UX_WorkflowTemplate
# Open http://127.0.0.1:8080/preview.html
```

No package installation or build step is needed to view the kit. Stop the local server with Ctrl+C.

**Figma:** [Open the detailed battle sheet](https://www.figma.com/design/cquf2cmlxA0uqGiCmBPi4k?node-id=10-4645), [chest flow](https://www.figma.com/design/cquf2cmlxA0uqGiCmBPi4k?node-id=10-2488), or [live-ops flow](https://www.figma.com/design/cquf2cmlxA0uqGiCmBPi4k?node-id=10-8644). [`FIGMA-INDEX.md`](FIGMA-INDEX.md) links directly to all 21 updated sheets.

## Reading the wireframes

- Phone frames are 390 × 844. Grayscale blocks represent game content; controls and text show the actual intended layout.
- Dark buttons are primary actions. Outlined buttons are alternatives.
- Each active control has a numbered badge. The adjacent route list names its destination screen ID; major buttons also have visible connector lines.
- Design rules and server outcomes are outside the phone, separated from player-facing copy.
- Stable screen IDs let you replace game terminology and art without losing the flow structure.
- Balances and timers are illustrative snapshots, not a continuously simulated wallet. Some selection, filter, toggle, and refresh controls remain on their current screen to represent a local state change.

## The player workflow

### 1. First-time user experience — `T01`–`T10`

Start → choose a name → select a card → deploy on a valid tile → complete a free coach battle → collect the first reward → instantly open a starter chest → receive copies → spend Gold on the first upgrade → arrive at the regular Battle hub.

Teach one mechanic at a time. Practice, retries, and the first chest are free. Persist the last completed checkpoint so an interruption does not restart the tutorial or duplicate rewards. Introduce tickets and timed chests after the player has experienced the core action and a useful upgrade.

### 2. Recurring battle loop — `B01`–`B10`

Battle hub → select mode → check deck, ticket balance, and chest capacity → reserve a ticket in matchmaking → consume it when the match starts → deploy cards using elixir → settle the result → collect rewards → return to the hub or improve the deck.

A queue cancellation or timeout releases the reserved ticket. A completed loss consumes it. A server-cancelled match refunds once. Free training remains available when tickets are depleted.

### 3. Chest progression — `H01`–`H12`

Earn a chest → place it in a slot → start a free unlock timer → wait or explicitly confirm a Gem speedup → chest becomes ready → open → reveal each reward → review the summary → free the slot → upgrade or start another chest.

Include the full-slot decision before battle, the one-active-timer conflict, optional reminders, reward probabilities, and interrupted reveals. Server time controls readiness. An opened chest's contents are granted once; resuming its animation must not reroll or regrant them.

### 4. Collection and upgrades — `D01`–`D14`

Inspect the deck and collection → open a specific card → compare current and next-level stats → check Gold and copies → confirm both costs → show the upgraded card → equip it or prepare for battle.

Keep the deck valid at eight unique cards. Missing Gold leads to earning options or a separately confirmed exchange. Missing copies lead to chests, clan requests, or progression gates. Gems never silently replace missing resources.

### 5. Purchases and currency recovery — `W01`–`W17`

View an offer or resource deficit → inspect quantity and full price → confirm the exchange or open the platform store → authenticate → verify the receipt → deliver the correct item → return to the original intent.

Cancellation leaves the wallet unchanged. A pending receipt is retried with the same transaction, not a second purchase. Returning from a Gem purchase must not automatically spend the new Gems. The platform sheets in this prototype are schematic and cannot charge money.

### 6. Live ops — `L01`–`L28`

Discover an event → check eligibility and rules → enter with the configured ticket cost → play in that event's context → settle score → claim milestones → inspect provisional rank → wait for final results → claim final rewards → move unclaimed grants to Inbox after the claim window.

The examples include Crown Rush, daily goals and gifts, a free/premium season pass, upcoming and locked events, premium entitlement verification, returner rewards, and Inbox delivery. Event queue, match, and result states preserve the event identity.

### 7. Clan and service flows — `S01`–`S06`, `R01`–`R09`

Discover and preview a clan → join → request or donate cards → contribute to a cooperative chest. Supporting flows cover moderation, emotes, multiplayer menus, reconnect, account linking, save conflicts, settings, purchase support, and optional reminders.

Multiplayer keeps running while a menu is open. Reconnect rejoins the same match without another ticket charge. Save conflicts show both progress snapshots and an explicit confirmation before replacement.

## Economy contract

| Resource | Typical sources | Uses and default example rules |
|---|---|---|
| **Gold — soft currency** | Battles, chests, quests, events, donations | Card upgrades; Gold and card copies deducted together after confirmation |
| **Gems — hard currency** | Configured rewards and platform purchases | Ticket refills, chest speedups, Gold exchanges; full cost and resulting balance shown |
| **Battle tickets — entry resource** | Regeneration, rewards, Gem refill | Cap 5; +1 per 30 minutes; 1 per ranked/event match; full refill from zero costs 20 Gems in the example |
| **Chests — reward containers** | Ranked wins, milestones, events | Four slots; one running timer; Silver Chest unlocks in 3 hours; waiting remains free |
| **Elixir — match resource** | Regenerates during a battle | Deploy cards from the hand; separate from the persistent wallet |
| **Card copies — progression material** | Chests and clan requests | Combined with Gold for card upgrades |

Ticket rewards may overflow the regeneration cap; regeneration pauses while at or above the cap. Guaranteed event chests can open immediately or be held in Inbox when slots are full. Configure these choices consistently before testing.

Tickets are a Royal Scibbles extension. The timed chest-slot model draws on **classic** Clash Royale; Supercell removed chest queues and timers in its April 2025 update. This kit does not reproduce current Clash Royale rules, odds, or prices.

## Live-ops production workflow

The player-facing screens need a matching operator workflow. See [`reference/G-Studio-Workflow.svg`](reference/G-Studio-Workflow.svg) and [`reference/studio-and-recipes.json`](reference/studio-and-recipes.json).

| Stage | Decision or output |
|---|---|
| Brief | Player objective, event owner, success measures, and stop conditions |
| Audience | Eligibility, enrollment, unlock gates, exclusions, and returning-player treatment |
| Economy | Score sources, caps, reward table, cost budget, ties, inventory overflow, and duplicate-grant protection |
| Schedule | Authoritative start/end timestamps, time-zone presentation, late-match grace, claim period, and expiry |
| Configure | Versioned rules, localized copy, surfaces, notifications, and complete reward previews |
| QA and staging | Rehearse boundary times, no tickets, full chests, disconnects, purchase cancellation, duplicate claims, and rollback |
| Launch and monitor | Track entry, score settlement, purchases, claims, delivery failures, and unexpected reward issuance |
| Close and reconcile | Stop new entry, finish eligible matches, settle ranks, deliver or mail unclaimed rewards |
| Rollback and compensation | Preserve earned entitlements; stop faulty new activity; issue compensation through deduplicated grants |
| Readout | Compare participation, completion, delivery quality, and economy effects; document the next change |

[`reference/J-Recipes-Cadence-Adapters.svg`](reference/J-Recipes-Cadence-Adapters.svg) supplies reusable recipes: daily/weekly quests, solo milestones, leaderboards, clan cooperation, season passes, limited challenges, token exchanges, and returner catch-up. These companion boards are from the earlier broad kit; the numbered v2 sheets in this folder are the detailed player-flow reference.

## Adapt this to another game

1. Duplicate the folder and identify one core player action and one progression goal.
2. Rename the game's entities, currencies, collection items, reward containers, and social group.
3. Configure resource sources, sinks, caps, regeneration, prices, failure rules, and overflow behavior. Replace every illustrative balance with a coherent scenario.
4. Replace the gameplay shell while retaining entry, rewards, purchases, claims, and recovery contracts.
5. Rework FTUE checkpoints around the new game's core input and first meaningful upgrade.
6. Select live-ops recipes and define eligibility, schedule, scoring, tie handling, settlement, and claim expiry.
7. Walk success, failure, depletion, cancellation, interruption, and expiry paths before applying visual styling.
8. Replace grayscale tokens and game-content blocks with the target game's design system after the flow is agreed.

| Reference pattern | Main substitutions |
|---|---|
| Clash Royale | Deck, towers, hand, elixir, trophies, cards, and chests |
| Brawl Stars | Hero/loadout, party, action HUD, mode rules, and mastery |
| Kingshot | Settlement, building prerequisites, workers, march/build queues, help and speedups |
| Candy Crush | Level map, board, moves, boosters, failure/continue states; tickets can become lives |
| Tennis Clash | Gear/loadout, court, tour entry, points, tournament stages, and reward bags |

See [`reference/I-Workflow.svg`](reference/I-Workflow.svg) for broad genre shells. These are adaptation patterns, not claims about the games' current features or balance.

## Files and regeneration

| File | Purpose |
|---|---|
| `preview.html` | Self-contained clickable screen navigation; flow-sheet images are relative files |
| `00-Start-Here.svg` | Economy and workflow contract |
| `01-*` through `07-*.svg` | Detailed FTUE, battle, chest, collection, economy, live-ops, clan/service sheets |
| `screens/*.svg` | Individual phone wireframes |
| `source/build.py` | Authoring source: screen layouts, copy, routes, and scenario branches |
| `source/render.py` | SVG export, flow-sheet composition, data export, and HTML preview generation |
| `workflow.json` | Generated screen/action/module inventory; edit the Python authoring source rather than this export |
| `FIGMA-INDEX.md` | Direct links to all updated Figma sheets |
| `figma-imports.json` | Original import node IDs and placement receipts; reimporting creates different IDs |
| `validation.json` | Validation evidence for the delivered export |
| `reference/` | Companion studio workflow, event recipes, cadence, and genre adapters |

Python 3 and its standard library are sufficient to regenerate local assets:

```bash
cd F2P_UX_WorkflowTemplate
python3 source/build.py
```

Edit `source/build.py` to change screens, targets, labels, or rules. Edit `source/render.py` to change the shared rendering and preview. Rebuild regenerates the SVGs, preview, inventory, and structural validation; it preserves this maintained README. It does not publish to Figma, update Figma node IDs, or repeat browser QA. If you remove or rename modules, remove their stale exported files as part of the change.

## Validation and Figma limitations

The delivered export has no unresolved destination IDs. SVG hotspot targets match the JSON inventory, controls remain inside phone bounds, and the sheets contain no raster UI screenshots. Browser checks covered the full FTUE; ranked battle → chest speedup → all reveals → upgrade; a 500-Gem purchase's matching delivery; and event-specific queue → match → milestone reward. All 21 sheets were imported successfully, and the detailed battle sheet was visually checked in Figma.

Figma's Starter MCP tool limit blocked native editing and prototype wiring during creation. The updated sheets are **SVG vector trees**, not native auto-layout component instances. Text may become outlines on import. Native Figma prototype links are not wired; use the HTML preview for clickable navigation. Import the SVGs into another Design file as references, then rebuild reusable components and native interactions if your project requires them.

## Primary references

- [Clash Royale: Gems & Gold](https://support.supercell.com/clash-royale/en/articles/gems-and-gold-8.html)
- [Clash Royale: April 2025 update](https://supercell.com/en/games/clashroyale/blog/release-notes/april-update/)

Royal Scibbles · Detailed UX v2 · October 20, 2026.
