# carabAoS

A toolbox for solving a variety of niche problems related to AoS (Warhammer: Age of Sigmar).

Carabaos are domestic swamp-type water buffalos, and ther name contains 'AoS' - it's a bad pun.

## Summary

### What is in the toolbox?

- [Army list classifier](#army-list-classifier)
- [Army list flattener](#army-list-flattener)
- [Army list parser](#army-list-parser)

### Who is this for?

These tools are written in Python (as opposed to Rust <3) for accessibility. If you are a hobbyist hacker, or even if you're just code-curious, hopefully each tool is easy enough to use directly. If you're a level above and want to integrate these into your own projects, hopefully the code is documented enough that you can ~~steal it~~ rewrite it in your language of choice or otherwise extend it.

### Why did I make this?

I have no plans to build nice user interfaces or host websites, so my goal is for these tools to provide value to the community through either private use, or as part of an existing (or upcoming) website - all I ask for in return is accreditation.

### How should the tools be used?

As alluded to, the ways I'd expect these tools to be used will require a bit of Python knowledge, albeit (hopefully) a small amount. From there, for direct use each tool includes a small how-to guide, and for remixing them into your own projects the code is documented and commented where relevant.


## Tools

### Army list classifier

Classify an army into an established archetype.

Referring to army lists by their archetype is common parlance amongst competitive players in particular, but many statistics are measured and reported at the faction level. This tool provides a robust and easy to use mechanism for automatically classifying an army list into a defined archetype.

The approach used, and guidance on parameter settings and data management are discussed [here](/doc/classification.md), and a practical example of using the tool is explained [here](/doc/how_to_classify.md).

### Army list flattener

Flatten an army into warscroll and enhancement counts.

Inspired by the section regarding 'inclusion rate' of warscrolls and enhancements in the first Warhammer community [AoS metawatch](https://www.warhammer-community.com/2022/09/29/metawatch-how-the-warhammer-age-of-sigmar-team-uses-tournament-data-to-balance-the-game/). Distilling a highly structured army list into a simple flattened count of warscrolls and enhancements makes for much simpler comparisons, but retains the essence of the army.

Reducing army lists to this flattened representation sits at the core of further analysis, forming a structure similar to a deck of cards.

A practical guide to flattening an army list can be found [here](/doc/how_to_flatten.md).

### Army list parser

Parse an army list into manipulable data classes. 

The parser works with army lists exported by the Warhammer community [warscroll builder](https://www.warhammer-community.com/warscroll-builder/), or following that format. 

The current feature set is the minimum to support the list flattener. However, since the parser is combinatorial, the building blocks are easily composed to extend the functionality.

The [parsec.py](https://github.com/sighingnow/parsec.py) parser combinator library is currently used as the basis for this tool. This style of parsing was chosen because only a subset of the information being parsed is actually used for list flattening.


## Data analytics goals

Coming to AoS from Hearthstone (the last game I took really seriously), I realised how spoiled the Hearthstone community is with clean data and statistical analysis. [HSReplay.net](https://hsreplay.net/) is continuously being fed granular, reliable data, which they can analyse to show amazingly useful statistics to players.

A realistic example in AoS terms would be something like comparing the win rates of an army archetype (e.g. Morathi and bow snakes) with one artefact changed between variants, against another specific faction (e.g. Nighthaunt), at tournaments where both players are at least 3-0. For fine tuning army lists these kind of statistics could be really helpful.

There are obvious issues AoS faces, due to its nature as a physical game as opposed to a digital game like Hearthstone, which prevent it from likely ever reaching the same level. However, we still have plenty of room to grow in this area as a community, through data collection and validation through to analytics tooling - the latter of which I am hoping this toolbox contributes towards, either directly or indirectly.