# carabAoS

A toolbox for solving a variety of niche problems related to AoS (Warhammer: Age of Sigmar).


## Summary

### What is in the toolbox?

- [Army list parser](#army-list-parser)
- [Army list flattener](#army-list-flattener)

### Who is this for?

These tools are written in Python (as opposed to Rust <3) for accessibility. If you are a hobbyist hacker, or even if you're just code-curious, hopefully each tool is easy to use and understand. If you're a level above and want to integrate these into your own projects, hopefully the code is documented enough that you can ~~steal it~~ re-write it in your language of choice.

### Why did I make this?

I have no plans to build nice user interfaces or host websites, so my goal is for these tools to provide value to the community through either private use, or as part of an existing (or upcoming!) website - all I ask for in return is accreditation wherever the tools are used.

### How should the tools be used?

As alluded to, the ways I'd expect these tools to be used will require a bit of Python knowledge, albeit (hopefully) a small amount. From there, for direct use each tool includes a small how-to guide (to-do!), and for remixing them into your own projects the code itself is documented.


## Tools

### Army list flattener

Flatten an army into warscroll and enhancement counts.

Inspired by the section regarding 'inclusion rate' of warscrolls and enhancements in the first warhammer community [AoS metawatch](https://www.warhammer-community.com/2022/09/29/metawatch-how-the-warhammer-age-of-sigmar-team-uses-tournament-data-to-balance-the-game/). Distilling a highly structured army list into a simple flattened count of warscrolls and enhancements makes for much simpler comparisons, but retains the essence of the army.

Reducing army lists to this flattened representation sits at the core of further analysis, forming a structure similar to a deck of cards.

### Army list parser

Parse an army list into manipulable data classes. 

The parser works with army lists exported by the warhammer community [warscroll builder](https://www.warhammer-community.com/warscroll-builder/), or following that format. 

The current feature set is the minimum to support the list flattener. However, since the parser is combinatorial, the building blocks are easily composed to extend the functionality.

The [parsec.py](https://github.com/sighingnow/parsec.py) parser combinator library is currently used as the basis for this tool. This style of parsing was chosen because only a subset of the information being parsed is actually used for list flattening.


## Data analytics vision

Coming to AoS from hearthstone (the last game I took really seriously), I realised how spoiled the hearthstone community is with clean data and statistical analysis. [HSReplay.net](https://hsreplay.net/) is continuously being fed granular, reliable data, which they can analyse to show amazingly useful statistics to players.

A realistic example in AoS terms would be something like comparing the win rates of an army archetype (e.g. Morathi and bow snakes) with one artefact changed between variants, against another specific faction (e.g. Nighthaunt), at tournaments where both players are at least 3-0.

There are obvious issues AoS faces, due to its nature as a physical game as opposed to a digital game like hearthstone, which prevent it from likely ever reaching the same level. However, we still have plenty of room to grow in this area as a community, through data collection and validation through to analytics tooling - the latter of which I am hoping this toolbox contributes towards, either directly or indirectly.