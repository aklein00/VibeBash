from pathlib import Path
import json, html, textwrap, math, re

OUT=Path(__file__).resolve().parents[1]; OUT.mkdir(exist_ok=True)
(OUT/'screens').mkdir(exist_ok=True)
SCREENS={}; MODULES=[]
INK='#252525'; MID='#747474'; LINE='#b4b4b4'; PAPER='#ffffff'; SOFT='#eeeeee'
def esc(v): return html.escape(str(v),quote=True)
def rect(x,y,w,h,fill=PAPER,stroke=LINE,r=8):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
def text(x,y,value,size=14,w=340,bold=False,color=INK,align='start'):
    parts=[]
    for para in str(value).split('\n'):
        lines=textwrap.wrap(para,max(5,int(w/(size*.53))),break_long_words=False,break_on_hyphens=False) or ['']
        for line in lines:
            parts.append(f'<text x="{x}" y="{y}" font-family="Inter,Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{align}">{esc(line)}</text>'); y+=size*1.35
    return ''.join(parts)
def path(d,stroke=MID,width=1.5):return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}"/>'
def module(key,title,summary,rule):
    m=dict(key=key,title=title,summary=summary,rule=rule,ids=[]); MODULES.append(m); return m
class Screen:
    def __init__(self,m,id,title,subtitle='',back=None,wallet=True,nav=None,balance=('1,250','150','5/5'),rule='',entry=''):
        self.id=id; self.title=title; self.subtitle=subtitle; self.rule=rule; self.entry=entry;self.module=m['key'];self.parts=[];self.actions=[];self.scenarios=[]
        SCREENS[id]=self;m['ids'].append(id)
        self.parts+=[rect(0,0,390,844,PAPER,INK,20),text(20,25,'9:41',12,90,True),text(370,25,'ROYAL SCIBBLES',10,160,True,align='end')]
        if wallet:
            for i,(label,val,target) in enumerate(zip(['GOLD','GEMS','TICKETS'],balance,['W01','W02','B08'])):
                x=16+i*122;self.parts+=[rect(x,40,114,54,SOFT,SOFT),text(x+9,57,label,10,80,True),text(x+9,78,val,17,80,True)]
                if label=='TICKETS': target='B08' if balance[2]=='0/5' else 'B10'
                self.hit(x,40,114,54,target,label.title()+' balance / +',badge=(x+101,78),kind='wallet')
        if back:self.btn(16,106,42,40,'‹',back,kind='back',desc='Back')
        self.parts.append(text(70 if back else 20,133,title,23,295 if back else 350,True))
        if subtitle:self.parts.append(text(20,162,subtitle,13,350,color=MID))
        if nav:
            self.parts.append(rect(0,770,390,74,SOFT,LINE,0))
            for i,(lab,to) in enumerate([('Shop','W01'),('Cards','D01'),('Battle','B01'),('Events','L01'),('Clan','S01')]):
                x=i*78; self.parts.append(rect(x+3,777,72,57,INK if lab==nav else PAPER,LINE,6));self.parts.append(text(x+39,817,lab,12,68,True,PAPER if lab==nav else INK,'middle'))
                self.hit(x+3,777,72,57,to,lab+' tab',badge=(x+61,790),kind='nav')
    def txt(self,y,value,size=15,bold=False,x=20,w=350,color=INK):self.parts.append(text(x,y,value,size,w,bold,color));return self
    def box(self,x,y,w,h,fill=SOFT,stroke=LINE):self.parts.append(rect(x,y,w,h,fill,stroke));return self
    def btn(self,x,y,w,h,label,target,primary=False,desc=None,kind='button',effect=''):
        self.parts.append(rect(x,y,w,h,INK if primary else PAPER,INK,8));self.parts.append(text(x+12,y+h/2+5,label,14,w-45,True,PAPER if primary else INK))
        self.hit(x,y,w,h,target,desc or label,kind=kind,effect=effect,dark=primary);return self
    def hit(self,x,y,w,h,target,label,badge=None,kind='button',effect='',dark=False):
        n=len(self.actions)+1; bx,by=badge or (x+w-14,y+14)
        self.actions.append(dict(n=n,label=label,target=target,x=x,y=y,w=w,h=h,kind=kind,effect=effect))
        self.parts.append(f'<g data-target="{esc(target)}" role="button" tabindex="0" aria-label="{esc(label)}" style="cursor:pointer"><title>{esc(label)} → {esc(target)}</title><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="transparent"/><circle cx="{bx}" cy="{by}" r="8" fill="{PAPER if dark else INK}"/><text x="{bx}" y="{by+3}" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="9" font-weight="700" fill="{INK if dark else PAPER}">{n}</text></g>');return self
    def row(self,y,title,detail='',target=None,label='Open',h=72):
        self.box(20,y,350,h,PAPER);self.txt(y+25,title,15,True,x=34,w=220 if target else 320);self.txt(y+48,detail,12,x=34,w=220 if target else 320,color=MID)
        if target:self.btn(272,y+14,84,h-28,label,target)
        return self
    def bar(self,y,label,value=.5,right=''):
        self.txt(y,label,13,True);self.parts.append(text(370,y,right,12,170,False,MID,'end'));self.box(20,y+12,350,10,SOFT,SOFT);self.box(20,y+12,350*value,10,INK,INK);return self
    def note(self,y,value):self.box(20,y,350,72,SOFT,SOFT);self.txt(y+25,value,13,x=32,w=326);return self
    def card(self,x,y,name,level='Lv 2',cost='3',target=None,selected=False,w=80,h=112):
        self.box(x,y,w,h,'#d4d4d4' if selected else PAPER,INK if selected else LINE);self.parts+=[rect(x+8,y+22,w-16,44,'#dedede',LINE,4),text(x+w/2,y+52,name[:1],25,50,True,align='middle'),text(x+7,y+16,cost,11,30,True),text(x+6,y+83,name,11,w-12,True),text(x+6,y+101,level,10,w-12,color=MID)]
        if target:self.hit(x,y,w,h,target,name,kind='card')
        return self
    def chest(self,x,y,state,target=None,timer='',w=80):
        self.box(x,y,w,119,PAPER);self.parts+=[rect(x+14,y+20,w-28,37,'#ccc',MID,5),path(f'M{x+14} {y+34} H{x+w-14}'),rect(x+w/2-5,y+30,10,13,'#777','#777',2),text(x+w/2,y+78,state,11,w-8,True,align='middle'),text(x+w/2,y+96,timer,10,w-8,False,MID,'middle')]
        if target:self.hit(x,y,w,119,target,state+' chest',kind='chest')
        return self
    def arena(self,y=190,teach=False,selected=False):
        self.box(20,y,350,330,'#e7e7e7',INK)
        self.parts+=[text(32,y+22,'RIVAL · Lv 2',12,160,True),text(356,y+22,'02:41',14,80,True,align='end')]
        for ty in [y+44,y+240]:
            for tx in [60,277]:self.parts+=[rect(tx,ty,54,45,'#bbb',MID,3),text(tx+27,ty+28,'T',18,40,True,align='middle')]
        self.parts+=[rect(168,y+35,55,51,'#999',INK,3),rect(168,y+254,55,51,'#999',INK,3),path(f'M20 {y+165} H370',MID,18),rect(80,y+152,50,26,'#ccc',INK,0),rect(260,y+152,50,26,'#ccc',INK,0)]
        if selected:self.parts+=[rect(28,y+186,334,51,'#fff',INK,5),text(195,y+217,'TAP TO DEPLOY HERE',13,300,True,align='middle')]
        for i,n in enumerate(['Knight','Archer','Giant','Zap']):self.card(20+i*89,y+344,n,cost=str([3,3,5,2][i]),target=('T04' if i==0 else None) if teach else 'B05',selected=(selected and i==0),w=82,h=112)
        self.bar(y+483,'ELIXIR',.7,'7 / 10 · refills in battle')
        return self
    def sim(self,label,target):self.scenarios.append(dict(label=label,target=target));return self
    def svg(self):return f'<svg xmlns="http://www.w3.org/2000/svg" width="390" height="844" viewBox="0 0 390 844">'+''.join(self.parts)+'</svg>'

# A / FIRST SESSION
m=module('01','FTUE · Learn → win → unlock → upgrade','10 wireframes · A free practice duel teaches deployment before tickets, chests and the full hub appear.','Persist the last completed tutorial checkpoint. Tutorial match, retry and first chest are free; do not spend tickets or gems.')
s=Screen(m,'T01','Welcome, Scribbler!',wallet=False,rule='New installation → choose a local starter profile. Continue is available without a network account.')
s.box(20,195,350,225,'#ddd').txt(285,'ROYAL\nSCIBBLES',36,True,x=60,w=290).txt(468,'Build a deck. Defend your towers.',21,True).txt(512,'A short practice battle will show you how to play. Your first rewards are free.',16).btn(20,625,350,54,'Start playing','T02',True).btn(20,693,350,48,'I already have an account','R03')
s=Screen(m,'T02','Choose your name','Step 1 of 5 · Meet your coach',back='T01',wallet=False,rule='Default valid name shown. Empty or rejected text stays here with inline feedback; edit before continuing.')
s.box(20,200,350,120).txt(235,'COACH',12,True).txt(268,'Let’s make your first deck.',20,True).txt(367,'Player name',13,True).box(20,386,350,56,PAPER,INK).txt(421,'Scribbler_01',17).txt(470,'3–16 characters · Change later in Settings',12,color=MID).btn(20,635,350,54,'Continue','T03',True).note(540,'Your coach will guide one battle. No tickets are used.')
s=Screen(m,'T03','Select a card','Step 2 of 5 · Training · FREE',wallet=False,rule='Only the highlighted Knight is enabled in tutorial. No competitive opponent or entry cost.')
s.arena(185,True).box(20,190,350,70,PAPER,INK).txt(215,'1  Tap Knight in your hand.',16,True,x=32,w=326).txt(240,'Cards cost elixir, which refills.',13,x=32,w=326)
# Disable tutorial non-Knight targets in route data / overlay by building them all as the same learn step; action is select.
s=Screen(m,'T04','Deploy your Knight','Step 2 of 5 · Training · FREE',wallet=False,rule='Selecting a card does not spend elixir. Tap a valid own-side tile to commit deployment.')
s.arena(185,True,True);s.hit(28,371,334,51,'T05','Deploy Knight to highlighted tile',kind='playfield',effect='Elixir 7 → 4');s.note(709,'Tap the highlighted area on your side of the river.')
s=Screen(m,'T05','Defend, then attack','Step 3 of 5 · Training · FREE',wallet=False,rule='Repeat deploy with timing. After the coach match ends, advance to reward. Retry stays free.')
s.arena(185,True);s.txt(399,'KNIGHT →',15,True,x=150,w=150).note(709,'Your units move and attack automatically. Protect your towers!').sim('Coach match won','T06').sim('Need another try','T03')
s=Screen(m,'T06','Your first victory!','Step 3 of 5 · Training complete',wallet=False,rule='Practice reward is granted once by tutorial checkpoint, including after reconnect.')
s.box(20,205,350,150).txt(264,'3  CROWNS  0',32,True,x=60,w=290).txt(325,'Training complete',16,x=104,w=230).row(393,'+250 Gold','Use Gold to upgrade cards.').row(479,'1 Starter Chest','Contains your first extra card copies.').btn(20,650,350,56,'Collect rewards','T07',True,effect='Gold +250; grant Starter Chest')
s=Screen(m,'T07','Open your first chest','Step 4 of 5 · Instant tutorial unlock',wallet=False,rule='Starter Chest skips its timer. Explain later chest timers only after this instant reward.')
s.chest(115,220,'READY',timer='Free',w=160).txt(405,'Starter Chest',25,True,x=84,w=280).txt(456,'Gold and cards are inside.\nTap to reveal your reward.',17,x=52,w=290).btn(20,647,350,56,'Open chest · FREE','T08',True)
s=Screen(m,'T08','New cards!','Step 4 of 5 · Rewards added',wallet=False,rule='Reveal is cosmetic. Grants are recorded once before animation; skipping never loses rewards.')
s.card(130,205,'Knight','+10 copies','3',w=130,h=112).row(360,'Knight copies','10 / 10 · Upgrade ready').row(446,'Gold +250','Gold balance: 500').btn(20,645,350,56,'Upgrade Knight','T09',True).btn(20,711,350,42,'View all rewards again','T08')
s=Screen(m,'T09','First upgrade','Step 5 of 5 · Spend Gold + card copies',wallet=False,rule='Tutorial upgrade cost 100 Gold + 10 copies. Confirm deducts both once; no gems required.')
s.card(145,205,'Knight','Lv 1 → 2','3',w=100).row(346,'More health','420 → 462  (+10%)').row(432,'More damage','80 → 88  (+10%)').row(518,'Upgrade cost','100 Gold + 10 Knight copies').btn(20,647,350,56,'Upgrade · 100 Gold','T10',True,effect='Gold 500 → 400; copies 10 → 0')
s=Screen(m,'T10','Ready for the arena','Tutorial complete · Knight is Level 2',wallet=False,rule='Grant first full ticket refill only once. Land on the normal hub with next goals and chest slots.')
s.card(145,205,'Knight','LEVEL 2','3',w=100).row(356,'5 / 5 battle tickets','One ticket per ranked match.').row(442,'4 chest slots unlocked','Win a chest, start its timer, then open.').row(528,'Next: win a ranked battle','Earn trophies, Gold and card rewards.').btn(20,648,350,56,'Go to Battle hub','B01',True)

# B / CORE
m=module('02','Core battle · Tickets → deck → queue → result','9 wireframes · Main hub, mode selection, preparation, matchmaking, actual battle HUD, results and ticket recovery.','One ticket is reserved in queue and consumed when the match starts. Queue cancel/timeout releases it; match loss consumes it; server-cancelled matches refund once.')
s=Screen(m,'B01','Royal Arena','Scribbler_01 · Level 2 · 320 trophies',nav='Battle',rule='Hub prioritizes one battle CTA, chest queue and live event. Wallet + routes open contextual resource screens.')
s.btn(20,184,230,48,'Trophy Road · 320','D06').btn(262,184,108,48,'Inbox','L12');s.box(20,248,350,188,'#ddd').txt(288,'ARENA 2',14,True,x=145,w=170).txt(333,'ROYAL GARDENS',25,True,x=66,w=290).txt(404,'Deck 1 · 8 cards · Avg elixir 3.4',13,x=54,w=300)
s.btn(20,449,350,52,'Battle · 1 ticket','B03',True).btn(20,511,170,40,'Modes','B02').btn(200,511,170,40,'Edit deck','D01')
for i,(state,to,timer) in enumerate([('Unlock','H01','3h'),('Unlocking','H02','02:14:32'),('Open','H04','Ready'),('Empty',None,'Win a battle')]):s.chest(20+89*i,570,state,to,timer)
s.btn(20,708,350,42,'Crown Rush · ends in 2d','L02')
s=Screen(m,'B02','Choose a mode','Tickets apply to ranked and event battles',back='B01',nav='Battle',rule='Training is free and grants no ranked/event rewards. Event entry preserves its event ID.')
s.row(200,'Ranked 1v1','1 ticket · trophies + chest','B03','Select',100).row(315,'Training','FREE · practice with your deck','T03','Train',100).row(430,'Crown Rush','1 ticket · earn event crowns','L02','View',100).note(560,'Ranked and events share your battle ticket balance.')
s=Screen(m,'B03','Ready to battle?','Ranked 1v1 · Royal Gardens',back='B01',rule='Validate ticket count, 8-card deck and chest capacity before reserving entry. Full slots offer explicit choice H07.')
for i,n in enumerate(['Knight','Archer','Giant','Zap','Goblins','Cannon','Fireball','Minions']):s.card(20+(i%4)*89,205+(i//4)*124,n,target='D02')
s.bar(479,'Deck complete · 8 / 8',1,'Avg elixir 3.4').row(521,'Entry: 1 ticket','5 available → 4 after match starts').row(606,'Chest slot available','Win reward will use slot 4.').btn(20,710,350,56,'Find opponent · 1 ticket','B04',True).sim('No tickets','B08').sim('All chest slots full','H07').sim('Deck incomplete','D05')
s=Screen(m,'B04','Finding opponent','Ranked 1v1 · Estimated wait: 10 sec',back=None,rule='Cancel releases reservation. A late match-found response wins only if server has committed start; otherwise cancel wins.')
s.box(20,205,350,250).txt(300,'YOUR DECK',26,True,x=106,w=260).txt(348,'vs',25,True,x=180,w=70).txt(402,'SEARCHING…',25,True,x=100,w=260).row(490,'1 ticket reserved','No ticket spent until battle starts.').btn(20,688,350,54,'Cancel matchmaking','B01').sim('Opponent found','B05').sim('Timeout: reservation released','R02')
s=Screen(m,'B05','Battle in progress','Ranked 1v1 · Ticket spent: 5 → 4',wallet=False,rule='Wallet is hidden in live play. Card selects then valid tile spends elixir; unavailable cards disabled. Menu never pauses multiplayer.')
s.arena(185,selected=True);s.hit(28,371,334,51,'B05','Deploy selected card',kind='playfield');s.btn(20,716,166,42,'Emotes','S05').btn(198,716,172,42,'Menu','R01');s.sim('Match ends: victory','B06').sim('Match ends: defeat','B07').sim('Connection lost','R02')
s=Screen(m,'B06','Victory!','3 crowns to 1 · Ranked result',balance=('1,250','150','4/5'),rule='Result settles trophies and reward grant once using match ID. Claim returns to hub; capacity is handled before queue.')
s.box(20,199,350,151).txt(262,'3  CROWNS  1',31,True,x=67,w=290).txt(318,'+30 trophies · 350 total',16,x=80,w=270).row(379,'+50 Gold','1,250 → 1,300').row(465,'Silver Chest earned','Slot 4 · 3 hour unlock').row(551,'+3 event crowns','Crown Rush: 3 / 10').btn(20,655,350,54,'Collect and view chest','H01',True).btn(20,719,350,42,'Back to Battle hub','B01')
s=Screen(m,'B07','Defeat','1 crown to 3 · Try a different approach',balance=('1,250','150','4/5'),rule='Ticket is consumed; no chest is earned. Event crowns from completed play may still count. Rematch revalidates ticket and deck.')
s.box(20,205,350,150).txt(267,'1  CROWN  3',31,True,x=70,w=290).txt(322,'−20 trophies · 300 total',16,x=78,w=280).row(391,'No chest this battle','Win a ranked match to earn one.').note(490,'Tip: wait for elixir before committing your whole hand.').btn(20,638,350,54,'Try again · 1 ticket','B03',True).btn(20,704,350,48,'Improve my deck','D01')
s=Screen(m,'B08','Battle tickets','0 / 5 · Next free ticket in 12:36',back='B03',balance=('1,250','150','0/5'),rule='Example economy: +1 ticket / 30 min up to 5. Buy only missing tickets; free training always available. Server validates refill amount and price.')
s.bar(208,'Tickets available',0,'0 / 5').box(20,253,350,98).txt(282,'Next ticket: 12:36',24,True,x=44,w=310).txt(321,'Fully refilled in 2h 12m',14,x=85,w=260).row(379,'Refill to 5 tickets','Cost: 20 Gems · You have 150').btn(20,487,350,54,'Refill · 20 Gems','B09',True).btn(20,555,350,50,'Play free training','T03').btn(20,620,350,50,'Return to Battle hub','B01').sim('Timer gives 1 ticket','B03').sim('Not enough Gems','W05')
s=Screen(m,'B09','Confirm ticket refill','Get back into battle',back='B08',balance=('1,250','150','0/5'),rule='Confirm uses current quote. If ticket regenerated, recalculate and request confirmation if price changes. Never silently overcharge.')
s.row(216,'Tickets','0 / 5 → 5 / 5').row(309,'Gems','150 → 130').note(414,'You are spending 20 Gems. Tickets refill for free over time.').btn(20,632,350,54,'Confirm · spend 20 Gems','B03',True,effect='Gems −20; tickets +5 capped at 5').btn(20,700,350,48,'Cancel','B08')

# CHESTS
m=module('03','Chest lifecycle · Earn → unlock → wait → reveal','10 wireframes · Locked, running, ready, speedup, queue conflict, full inventory and interrupted reveal.','Four slots; one running timer; default Silver Chest 3h. Free wait is always available. Server timestamp controls readiness; contents granted exactly once on open.')
s=Screen(m,'H01','Silver Chest','Slot 4 · Locked',back='B01',rule='Locked chest occupies one slot. Start unlock is free; if another is running, branch H08 without starting a second timer.')
s.chest(115,210,'LOCKED',timer='3h unlock',w=160).txt(382,'Contains',16,True).row(405,'Gold: 100–150','Soft currency for card upgrades.').row(491,'Cards: 10 common + 1 rare','Available cards depend on your arena.').btn(20,597,350,46,'View reward probabilities','H10').btn(20,655,350,54,'Start unlock · 3 hours','H02',True).btn(20,721,350,44,'Back to Battle hub','B01').sim('Another timer is active','H08')
s=Screen(m,'H02','Chest unlocking','Slot 4 · Silver Chest',back='B01',rule='Timer continues while offline. Push prompt is optional; returning after deadline opens Ready state. No need to keep the game open.')
s.chest(115,210,'UNLOCKING',timer='02:14:32',w=160).bar(386,'Time remaining',.25,'2h 14m').note(435,'Your chest unlocks while you are away. Only one chest can unlock at a time.').btn(20,550,350,52,'Finish now · 18 Gems','H03',True).btn(20,615,350,48,'Notify me when ready','R06').btn(20,680,350,48,'Keep waiting · back to hub','B01').sim('Timer reaches zero','H04').sim('Gem balance below 18','W05')
s=Screen(m,'H03','Finish unlocking?','Silver Chest · 2h 14m remaining',back='H02',rule='Gem quote is revalidated. If chest became ready during confirmation, charge zero and open Ready. Cancel preserves timer.')
s.chest(115,215,'UNLOCKING',timer='02:14:32',w=160).row(400,'Spend 18 Gems','150 Gems → 132 Gems').note(503,'The chest will be ready immediately. You can also wait for free.').btn(20,632,350,54,'Confirm · spend 18 Gems','H04',True,effect='Gems −18; chest ready').btn(20,700,350,48,'Keep waiting','H02')
s=Screen(m,'H04','Your chest is ready!','Slot 4 · Silver Chest',back='B01',rule='Open requests the server reward grant. Disable repeated taps while response is pending.')
s.chest(115,214,'READY',timer='Open now',w=160).txt(401,'Unlock complete',24,True,x=85,w=290).txt(450,'Your rewards are waiting.\nOpening this chest frees its slot.',17,x=50,w=290).btn(20,647,350,56,'Open chest','H05',True).btn(20,714,350,46,'Open later','B01')
s=Screen(m,'H05','Chest rewards','1 of 3 · Tap to reveal next reward',wallet=False,rule='Reward grant already committed. Skip reveals all; disconnect resumes reveal without rerolling contents.')
s.card(130,216,'Knight','+10 copies','3',w=130).txt(391,'Knight ×10',27,True,x=109,w=270).txt(439,'Card collection: 10 → 20',16,x=87,w=280).bar(505,'Revealed',.33,'1 / 3').btn(20,641,350,56,'Reveal next reward','H06',True).btn(20,711,350,46,'Skip animation · show all','H06').sim('App interrupted','H09')
s=Screen(m,'H06','Rewards collected','Silver Chest · Slot 4 is now empty',back=None,rule='Example contents: +120 Gold, +10 Knight, +1 Archer. Collection badges update; chest slot clears on confirmed grant.')
s.row(209,'+120 Gold','1,250 → 1,370').row(303,'Knight ×10','20 / 10 · Upgrade available').row(397,'Archer ×1','3 / 4 copies for next upgrade').btn(20,530,350,54,'Upgrade Knight','D02',True).btn(20,595,350,48,'Unlock another chest','H01').btn(20,660,350,48,'Back to Battle hub','B01')
s=Screen(m,'H07','Your chest slots are full','Choose what to do before battling',back='B03',rule='Do not silently discard an earned chest. Explicitly allow play without chest, or return to unlock/open. Trophies and Gold still count.')
for i,(a,b,t) in enumerate([('Unlock','H01','3h'),('Unlocking','H02','2h 14m'),('Open','H04','Ready'),('Unlock','H01','3h')]):s.chest(20+89*i,216,a,b,t)
s.note(386,'You can still battle for trophies and Gold, but this battle will not award a chest.').btn(20,524,350,54,'Open ready chest','H04',True).btn(20,594,350,50,'Battle without a chest','B04').btn(20,662,350,48,'Cancel · back to hub','B01')
s=Screen(m,'H08','One chest at a time','Another chest is already unlocking',back='H01',rule='Starting another chest is blocked; there is no paid hidden queue. Keep selected chest locked while current timer runs.')
s.row(214,'Slot 2 · Unlocking','2h 14m remaining','H02','View',100).row(331,'Slot 4 · Waiting','Silver Chest · 3h unlock',h=100).note(467,'Finish or wait for the active chest, then start this one.').btn(20,615,350,54,'View active chest','H02',True).btn(20,683,350,48,'Back to Battle hub','B01')
s=Screen(m,'H09','Rewards are safe','You opened this chest before reconnecting',wallet=False,rule='Resume committed reward set by chest ID. Never repeat the grant or reroll after a crash.')
s.row(225,'Chest opened successfully','Silver Chest · reward receipt saved.').row(322,'Rewards already added','120 Gold · 10 Knight · 1 Archer').btn(20,624,350,56,'See all rewards','H06',True).btn(20,695,350,48,'Back to Battle hub','B01')
s=Screen(m,'H10','Chest contents','Example table · Arena 2 Silver Chest',back='H01',rule='Illustrative guaranteed bundle, not Clash Royale odds. Publish complete per-item probabilities for randomized purchased rewards before purchase.')
s.row(214,'100–150 Gold','Guaranteed · amount uniform across 51 values.').row(306,'10 common cards','Knight 50% / Goblins 50% per draw.').row(398,'1 rare card','Archer 50% / Giant 50%.').note(506,'Cards can repeat. Arena eligibility is fixed when this chest is awarded.').btn(20,659,350,52,'Back to chest','H01',True)

# COLLECTION
m=module('04','Collection · Inspect → upgrade → build an 8-card deck','7 wireframes · Card grid, stats, costs, confirmation, missing resources, deck repair and trophy progression.','Upgrade requires Gold and copies; Gems never silently substitute. Deck selection validates eight unique cards. Power and reward gates are configurable.')
s=Screen(m,'D01','Cards & battle deck','Deck 1 · 8 / 8 cards · Avg elixir 3.4',nav='Cards',rule='Selecting a collection card opens its detail; deck edit uses explicit replace slot. Upgrade badges reflect affordability and copies.')
s.btn(20,190,106,40,'Deck 1','D01',True).btn(137,190,106,40,'Deck 2','D05').btn(254,190,116,40,'Edit deck','D05')
for i,n in enumerate(['Knight','Archer','Giant','Zap','Goblins','Cannon','Fireball','Minions']):s.card(20+(i%4)*89,245+(i//4)*124,n,target='D02')
s.bar(510,'Collection',.25,'8 / 32 unlocked').btn(20,545,170,42,'Sort: Level','D07').btn(200,545,170,42,'Filter cards','D07')
for i,n in enumerate(['Knight','Archer','Giant','Locked']):s.card(20+i*89,610,n,'10/10' if i==0 else '3/4',target='D02' if i<3 else 'D06')
s=Screen(m,'D02','Knight','Common · Melee troop · 3 elixir',back='D01',rule='Show present and next-level stats, copies and Gold requirement before purchase. Upgrade CTA blocked only if no valid resources.')
s.card(145,194,'Knight','Lv 2','3',w=100).row(327,'Health','462 → 508 at Level 3').row(415,'Damage per hit','88 → 97 at Level 3').bar(520,'Knight copies',1,'20 / 10').row(561,'Upgrade to Level 3','Cost: 400 Gold + 10 copies').btn(20,659,350,54,'Upgrade · 400 Gold','D03',True).btn(20,724,350,44,'Use in deck','D05').sim('Insufficient Gold','W04').sim('Insufficient copies','D07')
s=Screen(m,'D03','Confirm upgrade','Knight · Level 2 → Level 3',back='D02',rule='Deduct Gold and copies atomically; increment card level once. Client refreshes on stale inventory before resubmitting.')
s.row(216,'Gold cost: 400','1,250 → 850').row(310,'Knight copies: 10','20 → 10').row(404,'New stats','508 health · 97 damage').btn(20,628,350,56,'Confirm upgrade','D04',True,effect='Gold −400; copies −10; Knight +1 level').btn(20,699,350,48,'Cancel','D02')
s=Screen(m,'D04','Knight upgraded!','Level 3 · Ready for your next battle',balance=('850','150','5/5'),rule='Success persists after navigation. New card level reflected in active deck and battle preparation.')
s.card(135,224,'Knight','LEVEL 3','3',w=120).row(396,'Health 508','+46 health from this upgrade').row(490,'Damage 97','+9 damage per hit').btn(20,630,350,54,'Back to my deck','D01',True).btn(20,697,350,48,'Battle · 1 ticket','B03')
s=Screen(m,'D05','Edit battle deck','Tap a slot to replace it · Deck 2',back='D01',rule='Example slot selection. Replace keeps cards unique. Save disabled when fewer than eight valid cards; show inline reason.')
for i,n in enumerate(['Knight','Archer','Giant','Zap','Goblins','Cannon','Fireball','EMPTY']):s.card(20+(i%4)*89,208+(i//4)*124,n,target='D05',selected=(i==7))
s.txt(487,'Choose a replacement',17,True)
for i,n in enumerate(['Minions','Knight','Archer']):s.card(20+89*i,510,n,target='D01' if i==0 else 'D05')
s.note(644,'Select Minions to fill slot 8 and save this deck. Cards already used cannot be added twice.')
s=Screen(m,'D06','Trophy Road','Royal Gardens · 320 trophies',back='B01',rule='Claim once per milestone. Unlock gates depend on trophies and never auto-open a paid flow.')
s.row(206,'500 · Arena 3','Unlock 4 new collectible cards',h=90).row(312,'400 · Gold reward','500 Gold · 80 trophies to go',h=90).row(418,'300 · Milestone achieved','1 Silver Chest','H04','Claim',90).row(524,'200 · Claimed','250 Gold added earlier',h=90).btn(20,652,350,54,'Battle for trophies','B03',True)
s=Screen(m,'D07','Find cards','Collection filters and missing copies',back='D01',rule='Filter tabs stay local. Missing-copy branch points to earning sources; no direct gem substitution without an explicit offer.')
s.btn(20,202,106,42,'All','D01',True).btn(137,202,106,42,'Owned','D01').btn(254,202,116,42,'Locked','D06').row(280,'Knight · Need more copies','Earn cards from chest rewards.','H01','Chests',100).row(396,'Request from clan','Join a clan to request eligible cards.','S01','Clan',100).row(512,'Next arena unlocks','Play ranked to increase trophies.','D06','Road',100)

# WALLET
m=module('05','Economy · Soft currency, hard currency & purchase states','9 wireframes · Gold sources, Gem packs, platform checkout, shortfalls, verification, delivery and cancelled purchases.','Gold upgrades cards; Gems refill tickets, speed chests and buy explicit exchanges. Prices are illustrative. External checkout always returns verified entitlement or a recoverable pending state.')
s=Screen(m,'W01','Shop','Daily reset in 08:12:34',nav='Shop',rule='Show currency symbols and full quantities. Gold and Gems have distinct labels even in grayscale. No automatically selected purchase.')
s.row(196,'Daily free Gold','+100 Gold · 1 claim today','W07','Claim',90).row(302,'Gold pack','1,000 Gold · 60 Gems','W03','View',90).row(408,'Gem packs','Hard currency · local store prices','W02','Browse',90).row(514,'Season Pass','Premium reward track · ends in 12d','L08','View',90).btn(20,640,350,48,'Purchase history / help','R05')
s=Screen(m,'W02','Get Gems','Hard currency · choose a pack',back='W01',rule='Sample USD prices only; use localized platform catalogue. Purchased Gems do not grant battle power directly without an additional explicit action.')
s.row(204,'80 Gems','$0.99 · one-time purchase','W06','Buy',100).row(321,'500 Gems','$4.99 · one-time purchase','W06','Buy',100).row(438,'1,200 Gems','$9.99 · one-time purchase','W06','Buy',100).note(571,'Review the final price in the platform store before confirming.').btn(20,681,350,46,'Purchase help','R05')
s=Screen(m,'W03','Buy Gold','Exchange Gems for soft currency',back='W01',rule='Gems-to-Gold exchange is a one-time quoted transaction. Cancel returns unchanged; insufficient Gems sends W05 preserving return intent.')
s.row(215,'Receive','1,000 Gold').row(311,'Cost','60 Gems').row(407,'Balances after purchase','Gold: 2,250 · Gems: 90').btn(20,629,350,56,'Confirm · spend 60 Gems','W07',True,effect='Gems −60; Gold +1,000').btn(20,700,350,48,'Cancel','W01')
s=Screen(m,'W04','Not enough Gold','Knight upgrade costs 400 Gold',back='D02',balance=('250','150','5/5'),rule='Do not silently spend Gems to complete upgrade. Earn or exchange then return to card detail with fresh inventory.')
s.row(215,'You need 150 more Gold','250 available / 400 required').row(320,'Earn Gold in battle','Winning also earns a chest.','B03','Battle',100).row(437,'Open a ready chest','Gold and cards inside.','H04','Open',100).btn(20,594,350,54,'View Gold pack · 60 Gems','W03',True).btn(20,665,350,48,'Back to Knight','D02')
s=Screen(m,'W05','Not enough Gems','Example: ticket refill needs 20 Gems',back='B08',balance=('1,250','10','0/5'),rule='Preserve return_to and quoted product. A completed Gem purchase returns to the original confirmation; never auto-spend the new balance.')
s.row(218,'You need 10 more Gems','10 available / 20 required').note(329,'Tickets refill for free. Next free ticket arrives in 12:36.').btn(20,480,350,54,'View Gem packs','W02',True).btn(20,550,350,48,'Wait for free tickets','B08').btn(20,620,350,48,'Play free training','T03')
s=Screen(m,'W06','Confirm in the store','80 Gems · $0.99 USD example',back='W02',rule='OS-controlled purchase sheet is schematic. It requires platform authentication; demo controls simulate success/cancel/pending and never charge money.')
s.box(20,230,350,305,PAPER,INK).txt(268,'PLATFORM PURCHASE SHEET',12,True,x=40,w=310).txt(317,'Royal Scibbles',22,True,x=40,w=310).txt(359,'80 Gems',27,True,x=40,w=310).txt(402,'$0.99',24,True,x=40,w=310).txt(447,'Payment method managed by your store',13,x=40,w=310).btn(40,476,310,44,'Authenticate purchase','W08',True).btn(20,621,350,50,'Cancel purchase','W09')
s=Screen(m,'W07','Purchase delivered','Your wallet has been updated',rule='Receipt-specific summary must display actual items, cost and balances. Repeated delivery attempts are idempotent.')
s.row(220,'Example delivery: 1,000 Gold','Cost: 60 Gems · transaction RS-1024').row(318,'Gold balance','1,250 → 2,250').row(416,'Gem balance','150 → 90').btn(20,610,350,54,'Continue to previous action','D02',True).btn(20,679,350,48,'Back to Shop','W01')
s=Screen(m,'W08','Verifying purchase','Please wait · do not purchase again',rule='Platform success is not entitlement. Retry verification with same transaction; close keeps background reconciliation. Never ask for another payment.')
s.box(20,221,350,100).txt(279,'VERIFYING RECEIPT…',20,True,x=60,w=300).row(359,'80 Gems · $0.99','Your store purchase is being checked.').note(466,'If you close this screen, we will deliver your Gems after verification.').btn(20,599,350,52,'Check again','W08',True).btn(20,666,350,48,'Close · keep checking','B01').sim('Verified: deliver 80 Gems','W10').sim('Verification needs support','R05')
s=Screen(m,'W09','Purchase cancelled','No Gems were added',back='W02',rule='Cancelled/failed checkout never grants or charges in game. If platform reports charged, reconcile receipt instead of initiating a second purchase.')
s.row(229,'80 Gem purchase cancelled','Your in-game balance is unchanged.').btn(20,515,350,54,'Back to Gem packs','W02',True).btn(20,584,350,48,'I was charged · get help','R05').btn(20,652,350,48,'Back to Battle hub','B01')
s=Screen(m,'W10','Gems delivered','80 Gems added to your account',rule='Example checkout delivery. Preserve the original reason for purchase; refill is still explicitly confirmed on next screen.')
s.row(228,'+80 Gems','Purchase RS-1025 verified.').row(327,'Gem balance','10 → 90').note(436,'You can now return to your ticket refill. No Gems have been spent automatically.').btn(20,621,350,54,'Return to ticket refill','B09',True).btn(20,691,350,48,'Back to Shop','W01')

# LIVE OPS
m=module('06','Live ops · Discover → qualify → play → claim → settle','14 wireframes · Events, rules, milestone rewards, leaderboard, season pass, purchase branch, expiry, inbox and returner.','Event examples use shared tickets and event-specific scoring. Server start/end/claim deadlines and eligibility govern every entry, score and reward.')
s=Screen(m,'L01','Events','Season 4 · 12 days remaining',nav='Events',rule='Event hub order: claimable, active, upcoming, locked. Do not show every promotion as a blocking modal.')
s.row(196,'Crown Rush · LIVE','3 / 10 crowns · ends in 2d','L02','Play',94).row(306,'Royal Season Pass','Tier 3 · 1 free reward ready','L07','View',94).row(416,'Clan Chest Weekend','Starts tomorrow · cooperative','S04','View',94).row(526,'Grand Challenge · LOCKED','Requires Arena 3 / 500 trophies','L14','Why?',94).btn(20,654,350,48,'Daily quests & gift','L13')
s=Screen(m,'L02','Crown Rush','Ends in 2d 04h · Claim ends 24h later',back='L01',rule='First entry includes rules; recurring visits foreground progress. Completed battles grant crowns; late/disconnected results follow explicit policy.')
s.bar(210,'Event progress',.3,'3 / 10 crowns').row(259,'Next milestone: 5 crowns','+250 Gold','L04','View',90).row(365,'Final milestone: 10 crowns','1 Royal Chest','L04','View',90).row(471,'Your rank: #24','Top 10 reward: 500 Gold','L05','Ranks',90).btn(20,593,350,50,'Rules & rewards','L03').btn(20,658,350,56,'Play event · 1 ticket','L15',True)
s=Screen(m,'L03','How Crown Rush works','Active event · 2 days remaining',back='L02',rule='Display scoring, tie, entry, cap, reward and settlement policy. Example parameters are editable per event config.')
s.row(204,'Earn crowns','Each destroyed tower = 1 crown.').row(294,'Entry & daily limit','1 ticket per match · first 20 matches score.').row(384,'Rank & ties','More crowns wins; ties share reward rank.').row(474,'End & claim','Started before end? 5 min grace to finish.').row(564,'Claim window','Claim for 24h; unclaimed rewards go to Inbox.').btn(20,681,350,52,'Got it · return to event','L02',True)
s=Screen(m,'L04','Crown milestones','5 crowns earned · one reward ready',back='L02',rule='Claim once per event/milestone/player key. If inventory full, event chest opens instantly or is held in inbox; never silently dropped.')
s.row(205,'3 crowns · Claimed','100 Gold added earlier',h=90).row(311,'5 crowns · READY','250 Gold','L16','Claim',90).row(417,'10 crowns · Locked','Royal Chest · 5 crowns to go',h=90).bar(558,'Total event crowns',.5,'5 / 10').btn(20,657,350,54,'Keep playing · 1 ticket','L15',True)
s=Screen(m,'L05','Crown leaderboard','Your rank #24 · updates after matches',back='L02',rule='While active, rankings are provisional. Ties share rank reward; final server settlement determines grant.')
for y,t,d in [(205,'#1   InkKnight','45 crowns · reward: 2,000 Gold'),(285,'#2   PaperQueen','42 crowns · reward: 1,000 Gold'),(365,'#3   ScribbleFox','40 crowns · reward: 750 Gold'),(445,'#24  You','5 crowns · reward: 100 Gold')]:s.row(y,t,d,h=68)
s.note(545,'Final results are checked after the event ends. You will see a claim button when ready.').btn(20,665,350,52,'Back to Crown Rush','L02',True).sim('Event ends: settling','L06')
s=Screen(m,'L06','Calculating results','Crown Rush has ended',back='L01',rule='Disable score entry at deadline. Wait for late-match grace plus validation; show no premature final entitlement.')
s.row(218,'Your final score','5 crowns · rank verification in progress').row(318,'Results expected soon','Usually within 15 minutes').note(426,'You can leave this screen. We will send your reward to your Inbox when results are ready.').btn(20,581,350,52,'Refresh results','L06',True).btn(20,647,350,48,'Back to Events','L01').sim('Settlement complete','L10')
s=Screen(m,'L07','Royal Season Pass','Season 4 · 12d remaining · Tier 3',back='L01',rule='Two clearly separated tracks. Premium purchase unlocks eligible past tiers but does not automatically claim; free track remains usable.')
s.txt(205,'TIER',12,True,x=25,w=60).txt(205,'FREE',12,True,x=105,w=100).txt(205,'PREMIUM',12,True,x=235,w=120)
for i,(tier,free,prem) in enumerate([('4','500 Gold','Royal Chest'),('3','1 Ticket','80 Gems'),('2','250 Gold','1,000 Gold')]):
 y=228+i*122;s.box(20,y,350,106,PAPER);s.txt(y+42,tier,24,True,x=34,w=50);s.btn(85,y+13,125,80,free,'L16' if tier=='3' else 'L07');s.btn(225,y+13,130,80,prem,'L08')
s.bar(628,'Season progress',.6,'60 / 100 XP to tier 4').btn(20,683,350,54,'View Premium · $4.99','L08',True)
s=Screen(m,'L08','Upgrade Season Pass','Season 4 only · expires in 12d',back='L07',rule='Before real-money checkout show season expiry and eligible premium backlog. Example local price; no auto-renewal in this configuration.')
s.row(218,'Premium track rewards','Gems, Gold, chests and cosmetics.').row(312,'3 tiers ready to unlock','Claim rewards for tiers already reached.').row(406,'One-time purchase · $4.99','Applies to current season only.').note(513,'12 days remain to earn more tiers. Premium does not extend the season.').btn(20,640,350,56,'Continue to store · $4.99','L09',True).btn(20,709,350,46,'Keep free pass','L07')
s=Screen(m,'L09','Confirm Premium Pass','Season 4 · $4.99 USD example',back='L08',rule='Separate SKU from Gems. Entitlement verified before opening premium claims. Cancel or pending preserves free pass.')
s.box(20,219,350,255,PAPER,INK).txt(259,'PLATFORM PURCHASE SHEET',12,True,x=40,w=310).txt(307,'Season 4 Premium',24,True,x=40,w=310).txt(354,'$4.99 · one-time purchase',17,x=40,w=310).btn(40,399,310,48,'Authenticate purchase','L17',True).btn(20,584,350,48,'Cancel','L07').sim('Verification delayed','L18')
s=Screen(m,'L10','Final event reward','Crown Rush · Final rank #24',back='L01',rule='Claim leaderboard grant once; deadline 24h after end. After deadline send unclaimed reward to inbox using same grant key.')
s.box(20,219,350,139).txt(274,'RANK #24',33,True,x=100,w=290).txt(323,'5 crowns · Final result',16,x=100,w=280).row(405,'Your reward','100 Gold').txt(520,'Claim within 23h 59m',15,True,x=93,w=280).btn(20,637,350,56,'Claim 100 Gold','L16',True).btn(20,709,350,46,'Back to Events','L01').sim('Claim window expires','L11')
s=Screen(m,'L11','Event closed','Crown Rush is no longer active',back='L01',rule='Expired deep links never enroll the player. Automatic mail uses original event reward grant ID, not a duplicate new reward.')
s.row(226,'Your reward is in Inbox','100 Gold · available for 30 days').note(341,'This event has finished. View active events to find your next challenge.').btn(20,508,350,54,'Go to Inbox','L12',True).btn(20,578,350,48,'Browse active events','L01')
s=Screen(m,'L12','Inbox','Rewards and game messages',back='B01',rule='Inbox rewards have clear source and expiry. Claim idempotently; a full ticket balance permits reward overflow above regen cap.')
s.row(205,'Crown Rush reward','100 Gold · expires in 29d','L16','Claim',100).row(321,'Welcome back','2 tickets + 250 Gold · 6d left','L16','Claim',100).row(437,'Maintenance gift','1 chest · 29d left','H04','Open',100).btn(20,604,350,52,'Back to Battle hub','B01',True)
s=Screen(m,'L13','Daily goals','Resets in 08:12:34',back='L01',rule='Daily claims use reset instance IDs; no accidental streak loss from client time zone. Full ticket grants overflow cap; regen pauses above cap.')
s.row(204,'Daily gift · Ready','1 ticket','L16','Claim',90).row(309,'Play 3 battles','2 / 3 · Reward 100 Gold','B03','Play',90).row(414,'Open a chest','0 / 1 · Reward 50 Gold','H04','Open',90).row(519,'Upgrade one card','0 / 1 · Reward 1 ticket','D01','Cards',90).btn(20,658,350,48,'Back to Events','L01')
s=Screen(m,'L14','Grand Challenge','Unlock at Arena 3',back='L01',rule='Locked event is discoverable with a clear progress gate. No Gem bypass for arena eligibility in this configuration.')
s.box(20,211,350,127).txt(269,'LOCKED',32,True,x=121,w=240).txt(315,'Competitive challenge',16,x=97,w=290).bar(394,'Arena requirement',.64,'320 / 500 trophies').row(450,'Rewards preview','Gold and exclusive chest milestones').btn(20,616,350,54,'View Trophy Road','D06',True).btn(20,685,350,48,'Back to Events','L01')
s=Screen(m,'L15','Event battle ready','Crown Rush · 1 ticket · 3 / 10 crowns',back='L02',rule='Validate current event eligibility and deadline before reserving ticket. Event context remains attached through match and result.')
s.row(205,'Deck 1 ready','8 / 8 cards · Avg elixir 3.4','D01','Edit',90).row(316,'Match entry','1 ticket · 5 available').row(410,'Event scoring','Destroy towers to earn crowns.').note(515,'Results count if your match starts before event end and finishes within 5 minutes after.').btn(20,647,350,56,'Find event opponent','B04',True).sim('Event expired at entry','L11').sim('No tickets','B08')
s=Screen(m,'L16','Reward claimed','Added to your account',rule='Summary must use actual claim payload. Demonstration shows a milestone Gold claim; other reward types use the same receipt shell.')
s.row(228,'Crown milestone reward','+250 Gold').row(327,'Gold balance','1,250 → 1,500').btn(20,535,350,54,'Back to reward source','L04',True).btn(20,606,350,48,'Back to Battle hub','B01')
s=Screen(m,'L17','Premium unlocked','Season 4 · Tier 3 rewards available',rule='Premium entitlement enabled after verified receipt. Use the same claim keys for retroactive tier claims; do not grant twice.')
s.row(216,'Premium active','Expires with Season 4 in 12 days').row(314,'3 premium rewards ready','1,000 Gold · 80 Gems · cosmetic').btn(20,549,350,54,'View and claim rewards','L19',True).btn(20,620,350,48,'Back to Events','L01')
s=Screen(m,'L18','Verifying Premium Pass','Your purchase is pending',rule='Keep free track active while verification runs; retry same receipt. No second charge. Entitlement arrival produces L17.')
s.row(228,'Season 4 Premium','Receipt verification in progress').note(344,'You can leave safely. We will notify you when your Pass is ready.').btn(20,535,350,54,'Check again','L18',True).btn(20,606,350,48,'Back to free Pass','L07').sim('Receipt verified','L17').sim('Need support','R05')
s=Screen(m,'L19','Premium rewards','Tier 3 · Premium active',back='L01',rule='Claim each tier once. Clearly distinguish claimed, ready and locked progress states.')
s.row(218,'Tier 3 · 80 Gems','READY','L16','Claim',100).row(337,'Tier 2 · 1,000 Gold','READY','L16','Claim',100).row(456,'Tier 1 · Banner','READY','L16','Claim',100).btn(20,631,350,52,'Continue earning XP','L02',True)

# SOCIAL + SERVICE
m=module('07','Clan & service · Join, request, contribute and recover','12 wireframes · Clan discovery, requests, co-op chest, match menu, reconnect, account, settings, purchase support and reminders.','Social rewards share inventory and grant rules. Recovery never repeats ticket charges or reward grants. Multiplayer continues while menus are open.')
s=Screen(m,'S01','Clans','Find a team to trade cards and earn rewards',nav='Clan',rule='Preview before joining. Join requires eligibility and available slot; open clans join directly, invite-only clans show request pending.')
s.box(20,201,350,48,PAPER,INK).txt(232,'Search clan name…',15,color=MID);s.hit(20,201,350,48,'S01','Search clans')
s.row(273,'Royal Doodlers','42 / 50 members · Open','S02','View',100).row(389,'Ink Brigade','48 / 50 members · 500 trophies','S02','View',100).row(505,'Paper Knights','31 / 50 members · Open','S02','View',100)
s=Screen(m,'S02','Royal Doodlers','42 / 50 members · Open clan',back='S01',rule='Join checks capacity again. If full, show same view with inline reason and browse alternative clans.')
s.row(218,'Clan goals','Casual battles and weekly chest rewards.').row(312,'Entry requirement','200 trophies · You have 320').row(406,'Weekly activity','38 active members · Chest tier 3').btn(20,622,350,54,'Join clan','S03',True).btn(20,690,350,48,'Back to clans','S01')
s=Screen(m,'S03','Royal Doodlers','43 / 50 members · Clan chat',nav='Clan',rule='Card request cooldown and donation caps server-driven. Use preset messages in prototype; production text requires moderation/reporting.')
s.row(202,'InkKnight: Welcome!','2 minutes ago').row(294,'Archer request · 2 / 10','Donate 1 card · receive 5 Gold','S03','Give',100).row(410,'Clan Chest · 320 / 500','Contribute crowns together.','S04','View',100).btn(20,537,350,48,'Request Knight cards','S06').btn(20,602,350,48,'Quick message: Thanks!','S03').btn(20,667,350,42,'Report or mute a player','S05')
s=Screen(m,'S04','Clan Chest Weekend','Starts tomorrow · lasts 3 days',back='S03',rule='Upcoming state uses start timestamp. When active, only members enrolled before cutoff contribute; reward eligibility requires 5 personal crowns.')
s.row(216,'Team goal','Earn 500 crowns together.').row(313,'Your participation','Earn 5 crowns to qualify for the reward.').row(410,'Reward preview','1 Clan Chest per eligible member').btn(20,550,350,50,'Remind me when it starts','R06').btn(20,618,350,50,'Back to clan','S03').sim('Event is active','L02')
s=Screen(m,'S05','Player actions','InkKnight · clan member',back='S03',rule='Mute is local; report requires a reason and confirmation, then returns to context. Match emotes are contextual variants, not moderation UI.')
s.row(220,'Mute player','Hide chat and emotes from this player.','S03','Mute',100).row(337,'Report: harassment','Submit selected reason for review.','S03','Send',100).btn(20,594,350,50,'Cancel','S03')
s=Screen(m,'S06','Request cards','Knight · Common · 20 owned',back='S03',rule='One active request per player; cooldown 8h example. Cannot request locked or ineligible rarities. Claim donations once.')
s.card(140,219,'Knight','20 owned','3',w=110).row(387,'Request up to 10 copies','Clan members can donate eligible cards.').row(484,'Next request available','8 hours after this request').btn(20,632,350,54,'Post Knight request','S03',True).btn(20,699,350,48,'Cancel','S03')
s=Screen(m,'R01','Battle menu','The battle continues while this menu is open',wallet=False,rule='Multiplayer cannot pause. Leaving asks for explicit confirmation in production; reconnect may still rejoin if match remains active.')
s.note(215,'Your opponent can still attack. Return to battle to keep playing.').btn(20,353,350,54,'Return to battle','B05',True).btn(20,424,350,48,'Sound: On / Off','R01').btn(20,490,350,48,'Mute emotes','R01').btn(20,615,350,48,'Leave battle · accept defeat','B07')
s=Screen(m,'R02','Reconnecting…','Trying to restore your battle',wallet=False,rule='Rejoin same match ID; never consume another ticket. If match finished show authoritative result; server cancellation refunds once.')
s.box(20,221,350,110).txt(286,'CONNECTION LOST',23,True,x=69,w=290).note(385,'Your battle may still be running. Stay here while we reconnect.').btn(20,546,350,54,'Try reconnecting','R02',True).btn(20,616,350,48,'Back to Battle hub','B01').sim('Reconnected: match active','B05').sim('Match completed','B06').sim('Server cancelled: ticket refunded','B01')
s=Screen(m,'R03','Save your progress','Connect an account or continue as guest',back='B01',rule='Use platform identity. Conflicting saves need explicit selection with progress previews; never merge currency wallets blindly.')
s.row(219,'This device','Level 2 · 320 trophies · 8 cards').btn(20,346,350,54,'Connect game account','R07',True).btn(20,416,350,48,'Continue as guest','B01').note(525,'An account helps you restore your progress on another device.')
s=Screen(m,'R04','Settings','Preferences and account',back='B01',rule='Settings changes persist. Accessibility includes text/readability and reduced motion; permissions remain OS controlled.')
s.row(204,'Music / sound','On · tap to toggle','R04','Toggle',80).row(299,'Reduced motion','Off · minimize chest animations','R04','Toggle',80).row(394,'Save progress','Guest account','R03','Link',80).row(489,'Notifications','Chest ready and event reminders','R06','Edit',80).row(584,'Support','Purchase or gameplay issue','R05','Help',80)
s=Screen(m,'R05','Help & purchase support','Choose an issue',back='R04',rule='Support receives transaction IDs, not payment credentials. Recheck entitlement before suggesting another checkout. Example report is a local demo.')
s.row(208,'Purchase missing','Recheck store receipt and delivery.','W08','Check',100).row(324,'Chest reward missing','View saved reward receipt.','H09','View',100).row(440,'Battle connection issue','Recover match or report its ID.','R02','Open',100).note(565,'Reference: player RS-0001 · purchase RS-1025. Never share your payment password.')
s=Screen(m,'R06','Reminders','Choose what you want to hear about',back='R04',rule='Ask contextual permission only after user opts in. Denied permission falls back to in-game timers; do not repeatedly reprompt.')
s.row(215,'Chest is ready','One reminder per completed chest.').row(311,'An event is starting','Only events you choose to follow.').note(422,'Your device will ask whether Royal Scibbles can send notifications.').btn(20,565,350,54,'Enable reminders','R04',True).btn(20,635,350,48,'Not now','B01')
s=Screen(m,'R07','Choose saved progress','Two saves were found',back='R03',rule='Show both progress snapshots and last played date. Confirm replacement with explicit preview; server protects purchased entitlements during reconciliation.')
s.row(212,'This device · today','Level 2 · 320 trophies · 8 cards','B01','Keep',115).row(344,'Cloud save · yesterday','Level 5 · 1,200 trophies · 24 cards','R08','Load',115).note(513,'Choose the progress you want to continue. Currency balances will not be added together.')
s=Screen(m,'R08','Load cloud progress?','Replace this device’s active save',back='R07',rule='Explicit destructive-save confirmation; retain recovery snapshot. Entitlement reconciliation belongs to account service, not client totals.')
s.row(222,'Continue with cloud save','Level 5 · 1,200 trophies · 24 cards').note(334,'Your current local run will be replaced by this cloud save. This cannot be undone here.').btn(20,558,350,54,'Load cloud save','B01',True).btn(20,628,350,48,'Keep this device instead','R07')

def redirect(id,label,target):
    obj=SCREENS[id]
    for a in obj.actions:
        if a['label']==label:
            old=a['target'];a['target']=target
            for i,p in enumerate(obj.parts):
                if 'aria-label="'+esc(label)+'"' in p:
                    obj.parts[i]=p.replace('data-target="'+old+'"','data-target="'+target+'"').replace('→ '+old,'→ '+target)

# Explicit variants prevent generic confirmation screens from changing the user's purchase or reward.
m=MODULES[1]
s=Screen(m,'B10','Battle tickets','5 / 5 · Fully refilled',back='B01',rule='At cap, regeneration pauses and refill is unavailable. Reward-granted tickets may exceed this cap; do not discard them.')
s.bar(219,'Tickets ready',1,'5 / 5').row(283,'1 ticket per ranked/event match','Training is always free.').row(382,'Free refill','1 ticket every 30 minutes, up to 5.').note(490,'Your tickets are full. Play a battle to start the refill timer.').btn(20,626,350,54,'Prepare for battle','B03',True).btn(20,694,350,48,'Back to Battle hub','B01')
SCREENS['B01'].hit(20,106,350,62,'R04','Player profile / Settings',badge=(357,120),kind='profile')
m=MODULES[2]
s=Screen(m,'H11','Chest rewards','2 of 3 · Rare card',wallet=False,rule='Second reveal from the same immutable chest receipt; skip advances to summary without changing rewards.')
s.card(130,216,'Archer','+1 copy','3',w=130).txt(391,'Archer ×1',27,True,x=120,w=250).txt(439,'Card collection: 2 → 3',16,x=87,w=280).bar(505,'Revealed',.67,'2 / 3').btn(20,641,350,56,'Reveal final reward','H12',True).btn(20,711,350,46,'Skip animation · show all','H06')
s=Screen(m,'H12','Chest rewards','3 of 3 · Gold',wallet=False,rule='Final reveal before summary. Gold was granted once on opening, not again on this animation.')
s.box(115,215,160,130).txt(285,'+120',37,True,x=150,w=150).txt(322,'GOLD',15,True,x=170,w=120).txt(424,'Gold added to your wallet',20,True,x=66,w=290).bar(505,'Revealed',1,'3 / 3').btn(20,641,350,56,'See all rewards','H06',True)
redirect('H05','Reveal next reward','H11')
m=MODULES[4]
s=Screen(m,'W11','Daily Gold claimed','Come back after the next daily reset',rule='Daily gift uses a reset-instance claim key. Repeat taps and relaunch do not award it again.')
s.row(230,'+100 Gold','Daily shop gift added.').row(328,'Gold balance','1,250 → 1,350').btn(20,620,350,54,'Back to Shop','W01',True)
redirect('W01','Claim','W11')
# The Gem shop keeps one representative purchasable pack; larger options are documented as configurable catalogue rows.
for amount,price,id,pending,receipt in [('500','$4.99','W12','W14','W16'),('1,200','$9.99','W13','W15','W17')]:
 s=Screen(m,id,'Confirm in the store',f'{amount} Gems · {price} USD example',back='W02',rule='Pack ID and localized price are preserved through checkout and verification. Never substitute another pack after selection.')
 s.box(20,230,350,305,PAPER,INK).txt(268,'PLATFORM PURCHASE SHEET',12,True,x=40,w=310).txt(317,'Royal Scibbles',22,True,x=40,w=310).txt(359,amount+' Gems',27,True,x=40,w=310).txt(402,price,24,True,x=40,w=310).btn(40,476,310,44,'Authenticate purchase',pending,True).btn(20,621,350,50,'Cancel purchase','W02')
 s=Screen(m,pending,'Verifying purchase',amount+' Gems · receipt pending',rule='Retry verification of this same pack/transaction; close continues background delivery. Never charge again.')
 s.row(230,amount+' Gems · '+price,'Verifying your platform receipt.').note(345,'Do not purchase again. We will deliver your Gems after verification.').btn(20,590,350,52,'Check again',pending,True).btn(20,656,350,48,'Close · keep checking','B01').sim('Receipt verified',receipt)
 s=Screen(m,receipt,'Gems delivered',amount+' Gems added',rule='Delivery uses the same transaction ID and original pack. Return to prior action requires another explicit spend confirmation.')
 s.row(230,'+'+amount+' Gems','Verified store purchase: '+price).btn(20,590,350,54,'Return to ticket refill','B09',True).btn(20,660,350,48,'Back to Shop','W01')
for a,target in zip([a for a in SCREENS['W02'].actions if a['label']=='Buy'],['W06','W12','W13']):
 old=a['target'];a['target']=target
 # Route by button coordinate because the three row labels are deliberately identical.
 marker=f'x="{a["x"]}" y="{a["y"]}"'
 for i,p in enumerate(SCREENS['W02'].parts):
  if 'aria-label="Buy"' in p and marker in p:SCREENS['W02'].parts[i]=p.replace('data-target="'+old+'"','data-target="'+target+'"').replace('→ '+old,'→ '+target)
m=MODULES[5]
receipts=[('L20','Rank reward collected','100 Gold','L01'),('L21','Ticket claimed','1 battle ticket','L13'),('L22','Welcome-back reward','2 tickets + 250 Gold','B01'),('L23','Premium Gems claimed','80 Gems','L19'),('L24','Premium Gold claimed','1,000 Gold','L19'),('L25','Banner unlocked','Season 4 banner cosmetic','L19')]
for id,title,reward,back in receipts:
 s=Screen(m,id,title,'Reward added to your account',rule='Claim the original reward once. Ticket rewards may overflow the regeneration cap; already-claimed state replaces the button on return.')
 s.row(235,'Received: '+reward,'Your inventory has been updated.').btn(20,611,350,54,'Continue',back,True).btn(20,680,350,48,'Back to Battle hub','B01')
redirect('L10','Claim 100 Gold','L20')
for origin,targets in [('L12',['L20','L22']),('L13',['L21']),('L19',['L23','L24','L25'])]:
 for a,target in zip([a for a in SCREENS[origin].actions if a['label']=='Claim'],targets):
  old=a['target'];a['target']=target;marker=f'x="{a["x"]}" y="{a["y"]}"'
  for i,p in enumerate(SCREENS[origin].parts):
   if 'aria-label="Claim"' in p and marker in p:SCREENS[origin].parts[i]=p.replace('data-target="'+old+'"','data-target="'+target+'"').replace('→ '+old,'→ '+target)
redirect('L07','1 Ticket','L21')
s=Screen(m,'L26','Finding event opponent','Crown Rush · 1 ticket reserved',rule='Queue keeps event ID and scoring rules. Expiry before match start releases the ticket and returns to closed event.')
s.box(20,218,350,212).txt(289,'CROWN RUSH',26,True,x=88,w=290).txt(355,'Finding opponent…',19,x=94,w=280).row(474,'1 ticket reserved','No ticket consumed until start.').btn(20,657,350,52,'Cancel · return to event','L02').sim('Match starts','L27').sim('Event closes before start','L11')
s=Screen(m,'L27','Crown Rush battle','Event match · 1 ticket spent',wallet=False,rule='Score crowns for this event ID. Completed matches count within the 5-minute end grace; reconnect restores same match.')
s.arena(185,selected=True);s.hit(28,371,334,51,'L27','Deploy selected card',kind='playfield');s.note(710,'Destroy towers to earn event crowns.').sim('Battle complete: +2 crowns','L28').sim('Connection lost','R02')
for a in list(s.actions):
 if a['kind']=='card':redirect('L27',a['label'],'L27')
s=Screen(m,'L28','Crown Rush result','2 crowns earned · event progress updated',rule='Apply match score once. Display milestone reach after the score settles; return to the same event, not generic ranked mode.')
s.row(220,'+2 event crowns','3 → 5 crowns total').row(320,'Milestone reached','5 crowns · 250 Gold ready').row(420,'Ticket balance','5 → 4 tickets').btn(20,588,350,54,'Claim milestone reward','L04',True).btn(20,657,350,48,'Back to Crown Rush','L02')
redirect('L15','Find event opponent','L26')
m=MODULES[6]
s=Screen(m,'R09','Quick emotes','The battle continues',wallet=False,rule='Preset emote selection returns to the battle. Respect mute and emote rate limits; no chat moderation screen is shown here.')
for i,label in enumerate(['Good luck!','Well played!','Thanks!','Good game!']):s.btn(20+(i%2)*180,230+(i//2)*100,170,80,label,'B05')
s.btn(20,640,350,50,'Close emotes','B05')
redirect('B05','Emotes','R09')
# Other collection cards use their own detail variant; the Knight upgrade path remains the worked example.
m=MODULES[3]
for j,name in enumerate(['Archer','Giant','Zap','Goblins','Cannon','Fireball','Minions']):
 id='D'+str(8+j).zfill(2)
 s=Screen(m,id,name,'Card detail · Level 2',back='D01',rule='Reusable detail variant for selected card. This example is short of copies; show earning options and deck action rather than a misleading upgrade purchase.')
 s.card(140,205,name,'Lv 2','3',w=110).row(355,'Card copies','3 / 4 · Need 1 more copy').row(453,'Next upgrade','400 Gold + 4 copies').btn(20,576,350,54,'Find more copies','D07',True).btn(20,643,350,48,'Use in battle deck','D05').btn(20,708,350,44,'Back to collection','D01')
 for origin in ['D01','B03']:
  redirect(origin,name,id)

if __name__=='__main__':
    import render
    render.build(SCREENS,MODULES,OUT,rect,text,path)
