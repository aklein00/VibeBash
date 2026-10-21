import json,math,html,re,zipfile
def build(screens,modules,out,rect,text,path):
    esc=html.escape
    invalid=[(s.id,a['label'],a['target']) for s in screens.values() for a in s.actions+s.scenarios if a['target'] not in screens]
    if invalid:raise ValueError(invalid)
    route_count=sum(len(s.actions) for s in screens.values());sim_count=sum(len(s.scenarios) for s in screens.values())
    data={k:dict(id=s.id,title=s.title,subtitle=s.subtitle,rule=s.rule,module=s.module,actions=s.actions,scenarios=s.scenarios) for k,s in screens.items()}
    for s in screens.values():(out/'screens'/f'{s.id}.svg').write_text(s.svg())
    boards=[]
    for m in modules:
        # Keep boards practical to review: six full-size phones per board.
        chunks=[m['ids'][i:i+6] for i in range(0,len(m['ids']),6)]
        for part,ids in enumerate(chunks):
            W=2180; rows=math.ceil(len(ids)/3); H=400+rows*1170
            p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',rect(0,0,W,H,'#f4f4f4','#f4f4f4',0),text(40,48,'ROYAL SCIBBLES  /  DETAILED UX  /  v2',14,2000,True),text(40,98,m['title'],32,2080,True),text(40,139,f"Module {m['key']} · Sheet {part+1}/{len(chunks)} · {len(m['ids'])} states in this module · 390 × 844 mobile frames",16,2080),text(40,179,m['rule'],15,2080,color='#666')]
            p.append(rect(40,225,2100,80,'#fff','#ccc',6));p.append(text(60,252,'READ THE ROUTES',12,300,True));p.append(text(60,280,'Numbered controls match the route rail beside each phone. Arrows lead to destination screen IDs. Dashed paths are system outcomes, not player buttons.',15,2060))
            for i,id in enumerate(ids):
                s=screens[id]; x=40+(i%3)*710;y=360+(i//3)*1170
                p+=[text(x,y,id+'  /  '+s.title,20,670,True),text(x,y+28,s.subtitle or 'Player state',12,670,color='#777'),f'<g transform="translate({x},{y+50})">'+''.join(s.parts)+'</g>']
                ax=x+410; ay=y+65
                p.append(text(ax,ay,'CONTROL → DESTINATION',11,280,True));ay+=19
                # Every visible control has one explicit destination; high-count grids compress to 32px rows.
                rh=min(49,790/max(1,len(s.actions)))
                for j,a in enumerate(s.actions):
                    ly=ay+j*rh
                    p.append(rect(ax,ly,272,rh-4,'#fff','#ddd',4));p.append(text(ax+9,ly+14,f"{a['n']:02d}  {a['label']}",10,250,True));p.append(text(ax+27,ly+rh-10,'→ '+a['target']+' · '+screens[a['target']].title,10,235,color='#666'))
                    # Direct leaders for principal large controls; other controls use the same numbered key.
                    if a['kind']=='button' and a['w']>=300:
                        sy=y+50+a['y']+a['h']/2; ty=ly+rh/2
                        p.append(path(f'M{x+370} {sy} H{x+398} V{ty} H{ax}', '#8a8a8a',1));p.append(path(f'M{ax-5} {ty-4} L{ax} {ty} L{ax-5} {ty+4}','#8a8a8a',1))
                p.append(rect(x,y+914,682,146,'#e7e7e7','#e7e7e7',6));p.append(text(x+14,y+938,'STATE RULE & AUTOMATIC BRANCHES',11,650,True));p.append(text(x+14,y+963,s.rule,12,650,color='#555'))
                if s.scenarios:p.append(text(x+14,y+1030,'  /  '.join(a['label']+' → '+a['target'] for a in s.scenarios),11,650,True))
            p.append(text(40,H-40,'Graybox · Example economy values · Cards/Gold/Gems inspired by Clash Royale; ticket gating and timed slots are configurable Royal Scibbles mechanics.',12,2100,color='#777'));p.append('</svg>')
            name=f"{m['key']}-{part+1:02d}-{m['title'].split(' · ')[0].replace(' ','-').replace('&','and')}.svg";(out/name).write_text(''.join(p));boards.append(dict(file=name,title=m['title']+f' / {part+1}',ids=ids))
    # A compact reusable product contract board.
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="2180" height="2190" viewBox="0 0 2180 2190">',rect(0,0,2180,2190,'#f4f4f4','#f4f4f4',0),text(60,90,'ROYAL SCIBBLES',54,2050,True),text(60,142,'Detailed UX flow · Clash Royale–led graybox kit',30,2050,True),text(60,190,f'{len(screens)} distinct mobile states · {route_count} labeled control routes · {sim_count} system branches · {len(boards)} wireframe sheets',20,2050)]
    panels=[
      ('01  CORE LOOP','Choose an 8-card deck → spend 1 ticket on match start → deploy from a 4-card hand using regenerating elixir → win trophies, Gold and a chest → unlock the chest → collect cards → spend Gold + copies to upgrade.'),
      ('02  HOW TO READ / TEST','Dark filled buttons are primary actions. Each control has a numbered badge; the adjacent route rail names its exact destination. State rules sit outside the phone. Use the clickable HTML preview to walk any route; simulated match and timer outcomes sit outside the UI.'),
      ('GOLD / SOFT CURRENCY','Earn: battles, chests, quests, events, clan donations. Spend: card upgrades. Show cost, owned balance, deficit and new balance before confirmation. Missing Gold routes to earning options or an explicitly priced Gem exchange. No silent substitution.'),
      ('GEMS / HARD CURRENCY','Earn in configured rewards or buy from the platform store. Spend: ticket refills, chest speedups and Gold exchanges. Confirm amount and resulting balance. Preserve original intent after a purchase; do not automatically spend newly bought Gems.'),
      ('TICKETS / GAMEPLAY ENTRY','Example: 5 maximum, 1 ticket per 30 minutes, 1 per ranked/event match. Reserve in queue; consume on match start. Cancel or timeout releases reservation. Server-cancelled match refunds once. Reward grants may overflow cap; regeneration pauses at/above cap. Training is free.'),
      ('CHESTS / TIME-BASED UNLOCK','Example: four slots, one active timer, Silver Chest takes 3 hours. Win → locked → start timer → unlocking → ready → reveal → collected. Gems may finish early after confirmation. Full slots require explicit play-without-chest consent. Guaranteed event chests may open instantly or go to Inbox.'),
      ('FTUE / FIRST VALUE','One free practice duel → instant starter chest → card copies → Gold upgrade → grant full tickets → normal hub. Introduce one mechanic at a time. Persist checkpoint; all retries free. No monetization gates during teaching.'),
      ('LIVE OPS / PLAYER LIFECYCLE','Upcoming → eligible/locked → active → scoring → claimable milestones → results pending → final reward → claim deadline → Inbox. Include free and premium pass tracks, late-match grace, ties, daily claims and returner rewards.'),
      ('LIVE OPS / STUDIO WORKFLOW','Brief owner → audience + gates → scoring + economy budget → schedule in UTC → config + localized copy → QA boundary cases → staging rehearsal → publish/version lock → monitor entry/claims/grants → close + reconcile → analyze. Rollback stops new entry and preserves earned rewards; compensation uses a deduplicated grant.'),
      ('REUSE / SWAP THE CORE','Brawl-style: replace deck/arena with hero + action HUD. Kingshot-style: replace battle with build/march queues. Candy-style: replace hand/elixir with board/moves and tickets with lives. Tennis-style: replace deck with gear and arena with court. Keep resource, reward, claim, payment and recovery contracts.'),
      ('CONFIGURATION / BEFORE A TEST','Set ticket cap/regeneration/refill price; chest count/timers/reward table; card copy and Gold costs; trophy gates; event start/end/grace/claim dates; scoring caps; tie policy; pass price; notification frequency; account requirements. Sample numbers in these screens are not balance recommendations.'),
      ('DELIVERY / CURRENT LIMIT','The native Figma API is blocked by the Starter tool limit. These updated sheets are imported as vector trees, with visible routes. Native prototype wiring is not present. The supplied HTML preview is clickable and all target IDs are validated. Text behavior in Figma depends on SVG import.')]
    for i,(title,body) in enumerate(panels):
      x=60+(i%2)*1050;y=250+(i//2)*280;p.append(rect(x,y,1010,250,'#fff','#bbb',8));p.append(text(x+25,y+40,title,19,960,True));p.append(text(x+25,y+80,body,17,960,color='#555'))
    p.append(text(60,1990,'PRIMARY REFERENCE',14,2050,True));p.append(text(60,2027,'Supercell: Gems & Gold; Clash Royale April 2025 update. Current Clash Royale removed chest timers and queues in 2025. This kit deliberately combines classic chest progression with your requested ticket system.',17,2050,color='#555'));p.append(text(60,2125,'October 20, 2026 · Royal Scibbles is a generic product concept, not a recreation of current Clash Royale.',14,2050,color='#777'));p.append('</svg>')
    (out/'00-Start-Here.svg').write_text(''.join(p));boards.insert(0,dict(file='00-Start-Here.svg',title='Start here / economy contract',ids=[]))
    (out/'workflow.json').write_text(json.dumps(dict(screens=data,modules=modules,boards=boards),indent=2))
    (out/'validation.json').write_text(json.dumps(dict(screen_count=len(screens),control_route_count=route_count,system_branch_count=sim_count,broken_targets=invalid,board_count=len(boards),figma_native_prototypes=False,preview_type='Navigation prototype with illustrative state snapshots'),indent=2))
    svgs={id:s.svg() for id,s in screens.items()}
    preview='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Royal Scibbles · Detailed UX</title><style>
    *{box-sizing:border-box}body{margin:0;background:#ededed;color:#252525;font:14px Inter,Arial,sans-serif}header{background:#222;color:white;padding:20px 28px;display:flex;justify-content:space-between;align-items:center}h1{font-size:23px;margin:0 0 5px}header small{color:#ccc}button,select{font:inherit;padding:10px 12px;background:white;border:1px solid #aaa;border-radius:6px;cursor:pointer}button:hover{background:#ddd}main{display:grid;grid-template-columns:240px minmax(410px,1fr) 330px;gap:28px;padding:24px;max-width:1400px;margin:auto}nav{max-height:88vh;overflow:auto}nav h3{font-size:12px;text-transform:uppercase;margin:25px 0 9px}nav button{display:block;width:100%;text-align:left;margin:4px 0;font-size:12px}nav button.active{background:#252525;color:white}.phoneWrap{display:flex;justify-content:center;align-items:flex-start}.phone{width:390px;box-shadow:0 10px 40px #0002;border-radius:20px;overflow:hidden}.phone svg{display:block;width:100%;height:auto}aside{background:white;border:1px solid #ccc;border-radius:8px;padding:20px;align-self:start}aside h2{font-size:20px}aside p{line-height:1.6}aside button{display:block;text-align:left;width:100%;margin:7px 0;font-size:12px}.tag{font-size:11px;background:#eee;padding:6px;display:inline-block}.routes{max-height:450px;overflow:auto}.notice{padding:12px;border:1px dashed #888;background:#f2f2f2;font-size:12px;line-height:1.5}.boardview{display:none;padding:24px}.boardview img{width:100%;height:auto}.boardview select{margin-bottom:20px;min-width:400px}.toolbar{display:flex;gap:8px}#history{font-size:12px;line-height:1.5;max-height:110px;overflow:auto;color:#666}@media(max-width:1050px){main{grid-template-columns:1fr 320px}nav{display:none}}@media(max-width:760px){main{display:block;padding:12px}.phoneWrap{margin-bottom:20px}aside{max-width:390px;margin:auto}header{padding:14px}header small{display:none}}
    </style></head><body><header><div><h1>Royal Scibbles</h1><small>Detailed UX · Click numbered controls to follow routes · Graybox v2</small></div><div class="toolbar"><button id="toggle">View flow sheets</button><button id="reset">Start FTUE</button></div></header><main id="main"><nav id="nav"></nav><div class="phoneWrap"><div class="phone" id="phone"></div></div><aside><span class="tag" id="sid"></span><h2 id="title"></h2><p id="rule"></p><div id="scenarios"></div><h3>Button destinations</h3><div class="routes" id="routes"></div><h3>Route history</h3><div id="history"></div><p class="notice">Navigation prototype: balances and timers are illustrative screen snapshots. Outside-phone controls simulate match, timer and server outcomes. No real purchases or messages occur.</p></aside></main><div class="boardview" id="boardview"><select id="boards"></select><img id="board" alt="Detailed wireframe flow sheet"></div><script>
    const DATA=__DATA__,SVGS=__SVGS__,MODULES=__MODULES__,BOARDS=__BOARDS__;let current='',trail=[];
    const $=id=>document.getElementById(id);function el(tag,txt){const e=document.createElement(tag);e.textContent=txt;return e}
    function go(id){if(!DATA[id])throw Error('Unknown screen '+id);current=id;const s=DATA[id];$('phone').innerHTML=SVGS[id];$('sid').textContent=id+' · '+s.module;$('title').textContent=s.title;$('rule').textContent=s.rule;location.hash=id;trail.push(id);$('history').textContent=trail.slice(-12).join(' → ');$('routes').replaceChildren();s.actions.forEach(a=>{const b=el('button',String(a.n).padStart(2,'0')+' '+a.label+' → '+a.target);b.onclick=()=>go(a.target);$('routes').append(b)});$('scenarios').replaceChildren();if(s.scenarios.length){$('scenarios').append(el('h3','Simulate system outcome'));s.scenarios.forEach(a=>{const b=el('button',a.label+' → '+a.target);b.onclick=()=>go(a.target);$('scenarios').append(b)})}document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('active',b.dataset.id===id));}
    MODULES.forEach(m=>{$('nav').append(el('h3',m.title.split(' · ')[0]));m.ids.forEach(id=>{let b=el('button',id+' · '+DATA[id].title);b.dataset.id=id;b.onclick=()=>go(id);$('nav').append(b)})});
    $('phone').addEventListener('click',e=>{const g=e.target.closest('[data-target]');if(g)go(g.dataset.target)});$('phone').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){const g=e.target.closest('[data-target]');if(g){e.preventDefault();go(g.dataset.target)}}});
    $('reset').onclick=()=>{trail=[];go('T01')};let boardMode=false;$('toggle').onclick=()=>{boardMode=!boardMode;$('main').style.display=boardMode?'none':'';$('boardview').style.display=boardMode?'block':'none';$('toggle').textContent=boardMode?'View clickable screens':'View flow sheets'};BOARDS.forEach(b=>{const o=el('option',b.title);o.value=b.file;$('boards').append(o)});$('boards').onchange=()=>{$('board').src=$('boards').value};$('board').src=BOARDS[0].file;go(DATA[location.hash.slice(1)]?location.hash.slice(1):'T01');
    </script></body></html>'''
    preview=preview.replace('__DATA__',json.dumps(data)).replace('__SVGS__',json.dumps(svgs)).replace('__MODULES__',json.dumps(modules)).replace('__BOARDS__',json.dumps(boards));(out/'preview.html').write_text(preview)
    readme=f'''# Royal Scibbles — Detailed UX v2

{len(screens)} mobile wireframes, {route_count} labeled control routes, {sim_count} system branches, {len(boards)-1} flow sheets plus a reusable economy contract.

Open **preview.html** for the clickable navigation prototype. Use **View flow sheets** to see the full wireframes with numbered button destinations and direct leaders from major CTAs. Every screen is also a standalone SVG under `screens/`. All destinations were validated against `workflow.json`.

[Figma file](https://www.figma.com/design/cquf2cmlxA0uqGiCmBPi4k)

## What changed

This version replaces generic screen-card layouts with specific mobile UI: a battle hub with four chest slots; an arena with towers, river, deployment area, four-card hand and elixir; an eight-card deck; card stats and cost confirmations; locked/running/ready/reveal chest states; ticket recovery; Gold/Gem shops; platform checkout; event milestones, leaderboard and dual-track pass; clan and service screens.

The Figma Starter MCP limit still blocks native editing and prototype wiring. The v2 flow sheets can be imported as editable SVG vector trees. They are not native auto-layout component instances, and Figma prototype links are not wired. The HTML preview supplies the working navigation model; it is not a game/economy simulator. Some controls intentionally stay on their current state (filter/toggle/select patterns). Balances and timers are illustrative snapshots. SVG text may be converted to outlines by Figma.

## Default economy — configurable examples

| Resource | Sources | Sinks / rules |
|---|---|---|
| Gold (soft) | Battles, chests, quests, events, clan donations | Card upgrades; Gold + copies confirmed together |
| Gems (hard) | Reward configuration, platform store | Ticket refills, chest speedups, Gold exchange; explicit spend confirmation |
| Battle tickets | 1 per 30 minutes to a cap of 5; rewards; 20-Gem full refill from zero | 1 per ranked/event battle; reserve in queue, consume at match start; cancel releases, server cancellation refunds |
| Chests | Ranked wins and configured event/road rewards | Four slots, one active timer, Silver 3h; full-slot branch warns before battle; event rewards may open instantly or use Inbox |
| Elixir | Regenerates during a battle | Deploy cards; not purchasable through wallet |
| Card copies | Chests and clan requests | Upgrade costs combined with Gold |

Tickets are a Royal Scibbles extension. The chest slot/timer loop deliberately uses classic Clash Royale as inspiration; Supercell removed queues and timers in its April 2025 update. This kit does not claim to reproduce current Clash Royale rules, prices or reward odds.

## Adaptation workflow

1. Duplicate the kit; choose the primary gameplay shell.
2. Set all resource sources, sinks, caps, costs and overflow rules.
3. Set tutorial checkpoints and gates; keep tutorial retries free.
4. Configure chest slots, timers, reward tables and interrupted-open recovery.
5. Configure event eligibility, scoring, ties, timestamps, late-match grace, claims and expiry.
6. Replace only the gameplay/collection shell for another genre; retain payment, reward and recovery contracts.
7. Walk success, failure, depletion, cancellation, interruption and expiry routes before visual styling.

## Live-ops studio checklist

Brief → audience → economy budget → UTC schedule → versioned config + localized copy → QA → staging rehearsal → publish → monitor → close/reconcile → readout. Include explicit owner and rollback decision at each stage. Rollback stops entry while preserving already-earned rewards; compensation uses deduplicated grants. The original kit's studio and genre-adapter boards remain useful companions.

## Review paths

- FTUE: T01 → T02 → T03 → T04 → T05 → T06 → T07 → T08 → T09 → T10 → B01.
- Main loop: B01 → B03 → B04 → B05 → B06 → H01 → H02 → H04 → H05 → H06 → D02 → D03 → D04.
- Depletion: B03 → B08 → B09; insufficient Gems → W05 → W02 → W06 → W08 → W10 → B09.
- Chests: full slots H07; active unlock conflict H08; speedup H03; interrupted reveal H09.
- Live ops: L01 → L02 → L03 → L15; milestone L04; leaderboard L05 → L06 → L10 → L11 → L12.
- Pass: L07 → L08 → L09 → L18 → L17 → L19.

## Reference sources

- [Clash Royale Gems & Gold](https://support.supercell.com/clash-royale/en/articles/gems-and-gold-8.html)
- [Clash Royale April 2025 update](https://supercell.com/en/games/clashroyale/blog/release-notes/april-update/)

Version 2 · October 20, 2026.
'''
    if not (out/'README.md').exists(): (out/'README.md').write_text(readme)
    print(json.dumps(dict(screens=len(screens),routes=route_count,branches=sim_count,boards=len(boards),files=[b['file'] for b in boards]),indent=2))
