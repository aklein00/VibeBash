# Transcript: Claude Code + Obsidian agent setup

Spoken transcript of the video attached to [this X post](https://x.com/Nozelcode/status/2110712968682066237) by @Nozelcode (15 Oct 2026). The clip is 10 minutes 19 seconds. The speaker is Carson James, in his own vault, walking through how he runs Buckaroo Crew.

There is no official caption file on the post. This transcript was made from the audio with faster-whisper (`small`, English). Wording follows the audio. A few lines the model stumbled on are flagged at the bottom rather than silently rewritten.

On screen, after a revenue dashboard, he screen-shares an Obsidian vault named around Carson James: a Buckaroo Crew master note, a Jobs folder (Creating Campaigns, and notes for email and Facebook ads), and daily notes with an index at the top.

## 0:00 — Why he is showing this

If you've been using Claude Code for a while, you've probably seen videos that these people make about loops and agents and all this stuff. It's all really overcomplicated and overblown. I'm gonna show you how to actually do it really simple.

I'm not selling you anything. I make plenty of money. In fact, here's a screenshot showing you my monthly recurring revenue. I make about a hundred thousand dollars a month right now. All with AI, by the way, so I'm not just blowing smoke.

I'm gonna show you exactly what I do, how easy it really is, and basically make this not complicated at all, something that anybody could set up. The only thing that you have to have is an Obsidian vault.

## 0:40 — Organization and instructions, not a pile of notes

If you've been around Claude Code for a while, you've probably heard of people talking about Obsidian. It is very useful, but most people are using it the wrong way. They're just storing their notes or putting random stuff in there.

The key to using Obsidian and getting it to work, and having an agent that actually does things for you, or multiple agents, is organization. And then also, on top of that, you need instructions.

So instead of storing your Claude memory files in the directory that it puts them in by default, what I did is I took all of those Claude memory files and I brought them over into Obsidian. And they're named something awful, and the organization and structure is just chaotic. So I had Claude rename all of them, consolidate them, and I went from about 107 memory files to like 17 when it first started.

So it really helps to consolidate, and it makes your agent smarter and sharper too, because he's not scanning through hundreds of files now. It's just what's in your vault. Plus it's organized. You can find it. And you can see everything.

And so all the memories are always in your Obsidian. So you're not going to lose them. You can sync this with GitHub or wherever. And so everything that your agent knows is always backed up.

## 1:59 — One master note per folder, linked to the rest

So let me show you how it works. Now, obviously, I'm not going to go through every single file. That would take forever. But I'll show you an example.

So this is one of my businesses right here. It's Carson James, number two in the vault here. And under Carson James, my main product is called Buckaroo Crew. So I have a folder called Buckaroo Crew, and then I have a master file called the same thing as the folder. It's called Buckaroo Crew.

Now, what the master file is: it is an overview of everything else in the folder, and it's all wiki-linked to the other notes. So essentially my agent can go in and read this Buckaroo Crew note, and it sends him on somewhat of a wild goose chase, because he's gonna follow all of the wiki links. And by the time he's done going through this note, you'll have read every single note in this folder.

So part of the process that I'm about to show you — the first one of the steps in the process — is go read the Buckaroo Crew note, which then makes him read all the other notes. So you can see that by the time my agent is done, he is fully caught up with the entire business and this entire product.

So the main note here, Buckaroo Crew, like I said, links to all these other notes that the agent can go read about every single aspect or feature with this product called Buckaroo Crew.

## 3:29 — Jobs are the same pattern

Now, let me show you an example. I have a folder down here called Jobs. And in this folder I have different jobs right now. For example, I have creating campaigns, drafting emails, and Facebook ads.

So let's say I wanted to create a campaign. And a campaign for me is essentially setting up the offer, setting up the sales page, the order forms, all that stuff. So just like my structure up here, I have a file in Creating Campaigns, a markdown file called Creating Campaigns. And then what the agent does is it reads this file. This is like the main index file of this folder. Works the same exact way.

He goes and he reads through this one note, and by reading this one note it also sends him to read all the other notes in that Creating Campaigns folder. So by the time he's done, he knows exactly how to create a campaign.

So you can see right here, this note is linked to Buckaroo Crew, which is the note I showed you earlier. So this is in here as well. So by reading this one note, he's reading everything in this folder, and then he's also reading everything in the Buckaroo Crew folder. So he has full context of the product, to the features, in addition to knowing how to create a campaign.

So these are his steps. One, two, three, four, five, six, seven. So there's only eight steps in this one master note, this index note. But each of those steps leads to different notes, which then lead to different notes, which then lead to different notes.

Now, I don't know if this is the loop that everyone's talking about. I think it's kind of like that, but it works really well for me.

So now when I boot up my agent, I just say, "Hey, we're going to create a campaign. We're going to do this offer." And that's all I have to say. He comes back and he's like, the campaign's made, here's the page, etc.

So that's just one job. And then I have another job, creating Facebook ads. Drafting emails. It works the same exact way. I say, "Hey, we need to run some Facebook ads for this." He doesn't read the note and he does it. [See note A.]

## 5:45 — CLAUDE.md, MEMORY.md, and the anti-bloat rule

So the way that this works is, with Claude, you have two important files with Claude Code. You have the CLAUDE.md file, which is essentially just the "this is how we operate" file. Then you have the MEMORY.md file, and the memory file is how Claude Code defaults. That's like where they put all the memories.

But what you do is you modify that MEMORY.md file and you say, all of your memories live in the vault now. You give a pointer over to where the vault is. And then — instead of updating the memory, and you put these rules in your CLAUDE.md file, by the way — instead of updating a memory file or creating a new memory file when there's new data or there's something else to log, they do it here in the vault.

So my rules are, for example: only make a new note if it's completely, absolutely necessary. Try your best to append existing notes. The reason for that is so that I don't get bloat. So my CLAUDE.md is very much like anti-bloat. Everything you can to avoid bloat, which is just one of — I have a lot of rules in there, but that's one of the most important ones.

## 7:01 — Daily notes, written by the agent, with an index

Now the next thing, and some people already do this, but I'll show you the way I do it. The next thing that makes this really, really useful is your daily notes. So at the end of every session, the end of every day, and actually in the middle of sessions if you've just done something really big, I have my agent make a daily note.

And so I have all of these notes up here for everything that I do every single day. And I don't write these at all. My agent writes them. It's the day, the time, and then goes through, here's what we did that day. So everything that we do is always kept up with. It's never lost.

And anytime that he needs to find something — let's say I need to remember something we did, or I don't remember how we did this, or even I don't remember when we started doing this — they can search these notes really fast, especially before Madam, like this. [See note B.]

So I have the detailed notes below, but at the top of every daily note I have my agent do an index at the top. Instead of having to browse the entire note, my agent can go and scan the index of each note and get results that much faster. So he doesn't have to read the entire note to know what's in it. He gets a hit on the index, then he can dive down deeper into the note and find the actual context of what we're doing.

So that, combined with your processes and procedures, or your standard operating procedures, or whatever you call them, makes your agent really powerful. And that's how you get your agent to actually work for you.

You don't need all this stuff like OpenClaw and all this other bullshit that people are advertising. Let's do it like this. Do it like this. Set up your API credentials, your MCPs, and you have got a fully working autonomous agent.

## 9:03 — How multiple sessions stay in sync

Now, one of the byproducts of this that's really nice is that if you have multiple agents — I'll only use one, but I can run him in multiple sessions, so I can actually have my one agent run however many times I want him to run — but I do have another agent or another project, and they kind of sometimes mix tasks and what they're doing.

Well, the nice thing about this is that the other agent has similar instructions to this agent. So when one agent updates a daily note and logs what's going on, the other agent can see it too. So this is a way for multiple agents to talk to each other, communicate, make sure they're not doing something that's affecting something the other agent has already done. It gives them more context.

So if you've worked with Claude Code very long at all, you know that giving context is very important. Context is king. So that really helps too. So all of your agent's memories in a vault together is extremely useful.

And I haven't found the need to really have anything else besides this in order to get everything I want done. It's very fast. It's very efficient. And it works. So try it out.

## Notes on the audio

- **A (about 5:42).** The model consistently heard "He doesn't read the note and he does it." That clashes with the rest of the video, where the job is to read the index note and follow its links. It may have been "he then reads the note" or "he does read the note." The words were left as heard.
- **B (about 8:03).** "Especially before Madam, like this" is unclear on the audio. Left as heard. The next sentences are clear: detailed notes below, an index at the top, scan the index before reading the whole note.
- "You'll have read every single note" is what he says. In context he means the agent has read the folder by following the links.
- "OpenClaw" is the product name he dismisses. Earlier "Claude" was misheard as "claw" on the first pass and corrected on a second pass with a Claude/Obsidian prompt.
