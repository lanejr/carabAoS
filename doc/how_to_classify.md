# How to Classify Army Lists

This document will loosely guide a user through one approach for setting up a knowledge bank, tuning parameters, and classifying some army lists, all with the `army_classifier` tool. We will focus on some 'Maggotkin of Nurgle' armies as a worked example, these will inevitably be out of date but hopefully illustrative nonetheless. This guide may appear long due to all of the embedded army lists, but the content is kept concise.

## Decide on an Approach

There are a variety of approaches that the classifier tool supports, centering around how the training data set (knowledge bank) is built and maintained, and the classifier parameters chosen. These are described and explained in more depth [here](classification.md).

For our worked example we will choose an approach where our knowledge bank consists of prototype army lists only. Therefore we will take 'k' as `1`, expecting only a single very close neighbour data point for each classification; keep distance weighting disabled as it has no effect when looking at a single neighbour; and set warscroll weight to `1` and enhancement weight to `0`, i.e. enhancements carry no weight during comparisons, just to keep things simple.

The meaning of some of these choices will become clearer as we work through our example, or by reading the linked explanatory document.

## Build the Initial Knowledge Bank

Now we have an idea about how our knowledge bank will be set up, maintained, and used to classify new data, we can go ahead and start building.

For our Maggotkin of Nurgle example, we will identify two archetypes into which we want to classify new army lists: `Flies` and `Rot Coven`. 

Let's first set up our empty knowledge bank and add our two archetypes:
```
>>> from army_classifier import *
>>> bank = KnowledgeBank({})
>>> rot_coven = Archetype(faction = Faction(name = 'Maggotkin of Nurgle'), name = 'Rot Coven')
>>> flies = Archetype(faction = Faction(name = 'Maggotkin of Nurgle'), name = 'Flies')
>>>
```

Next, for our approach of using prototype data points, we need to define a prototype army list for each archetype. As a kind of 'training data' we will look at two real army lists <sup>[1](#list-1), [2](#list-2)</sup> - these will guide our prototype definitions.

To get our army lists in a flattened format for insertion into the knowledge bank, we can use the `army_flattener` tool - guidance is given [here](how_to_flatten.md) for how to do this. Once we have our flattened list, we can remove the warscrolls and enhancements we've decided to ignore for our prototype. Alternatively, these could be hand-written.

### Create the Prototypes

First looking at the `Rot Coven` list <sup>[1](#list-1)</sup>, we use our prior knowledge of the game and how the army plays to distill its essence down to the three `Rot Coven Rotringer Sorcerers`, and the three endless spells.

`Rot Coven` Prototype:
```
FlatArmyList(
    faction = Faction(name = 'Maggotkin of Nurgle'),
    warscrolls = [
        Warscroll(name = 'Rot Coven Rotbringer Sorcerer', count = 3),
        Warscroll(name = 'Umbral Spellportal', count = 1),
        Warscroll(name = 'Ravenak’s Gnashing Jaws', count = 1),
        Warscroll(name = 'Shards of Valagharr', count = 1),
    ],
    enhancements = [],
)
```

Next, for the `Flies` list <sup>[2](#list-2)</sup>, again we use our prior knowledge to make the decision to extract only the `Lord of Afflictions` and four units of `Pusgoyle Blightlords` (including reinforcement) as the core of this archetype.

`Flies` Prototype:
```
FlatArmyList(
    faction = Faction(name = 'Maggotkin of Nurgle'),
    warscrolls = [
        Warscroll(name = 'Lord of Afflictions', count = 1),
        Warscroll(name = 'Pusgoyle Blightlords', count = 4),
    ],
    enhancements = [],
)
```

### Evaluate the Prototypes

Our goal with prototype creation is to define data points that will accurately classify any new army lists, so reducing 'noise' from non-essential warscrolls will help massively. As an example, the `Rot Coven` list <sup>[1](#list-1)</sup> contains `Pusgoyle Blightlords` as well, however they are not fundamental to the army's behaviour - it would play similarly if they were substituted for another unit. Including them in our prototype would just create noise, and blur the line between our two archetypes. The key here is carving away any pieces that are not essential to the army's playstyle.

As a rule of thumb it is good to keep the sizes of competing prototypes similar - we can see the total count of features for our `Rot Coven` prototype is `6`, and for our `Flies` prototype is `5`. We'll explore an example [later](#a-naive-approach) where a dissimilar count causes classification issues.

### Add the Prototypes to the Knowledge Bank

Now we can add our prototypes to our empty knowledge bank:
```
>>> rot_coven_proto = FlatArmyList( ... paste prototype here ... )
>>> add_to_bank(archetype = rot_coven, army_list = rot_coven_proto, bank = bank)
>>> flies_proto = FlatArmyList( ... paste prototype here ... )
>>> add_to_bank(archetype = flies, army_list = flies_proto, bank = bank)
>>>
```

The current state of the knowledge bank should be printed after each addition, but to double check everything worked we can print the current knowledge bank explicitly:
```
>>> print(bank)
KnowledgeBank(
    data = {
        Archetype(faction = Faction(name = 'Maggotkin of Nurgle'), name = 'Rot Coven'): [
            FlatArmyList(
                faction = Faction(name = 'Maggotkin of Nurgle'),
                warscrolls = [
                    Warscroll(name = 'Ravenak’s Gnashing Jaws', count = 1),
                    Warscroll(name = 'Rot Coven Rotbringer Sorcerer', count = 3),
                    Warscroll(name = 'Shards of Valagharr', count = 1),
                    Warscroll(name = 'Umbral Spellportal', count = 1)
                ],
                enhancements = []
            )
        ],
        Archetype(faction = Faction(name = 'Maggotkin of Nurgle'), name = 'Flies'): [
            FlatArmyList(
                faction = Faction(name = 'Maggotkin of Nurgle'),
                warscrolls = [
                    Warscroll(name = 'Lord of Afflictions', count = 1),
                    Warscroll(name = 'Pusgoyle Blightlords', count = 4)
                ],
                enhancements = []
            )
        ],
    }
)
>>> 
```

Additionally, the setup we've done so far works well for incrementally building a knowledge bank (especially programatically), but we can very quickly build a knowledge bank in one step using the value of the `data` item, as printed above. 

For example:
```
>>> bank = KnowledgeBank(data = { ... paste data here ... })
>>>
```

## Classify some Army Lists

With our parameters chosen and knowledge bank created, we are ready to start classifying army lists into archetypes.

### Test the Classifier

Now is a good time to test the knowledge bank we've created in combination with our chosen parameters. The only inputs for classification are the knowledge bank, the army list we want to classify, and our parameters - so classification is only as good as our knowledge bank and parameter setup!

For our example we can classify the test army lists from which we derived our prototypes, in their flattened format.

First the `Rot Coven` list <sup>[1](#list-1)</sup>:
```
>>> classify(army_list = list1, bank = bank, k = 1, dist_weighted = False, war_weight = 1, enh_weight = 0)
Archetype(faction=Faction(name='Maggotkin of Nurgle'), name='Rot Coven')
>>>
```
which we see is correctly classified.

And next the `Flies` list <sup>[2](#list-2)</sup>:
```
>>> classify(army_list = list2, bank = bank, k = 1, dist_weighted = False, war_weight = 1, enh_weight = 0)
Archetype(faction=Faction(name='Maggotkin of Nurgle'), name='Flies')
>>>
```
which is also correctly classified.

### Classify a New Army List

Let's now use our classifier on some 'unseen' data outside of our mini 'training data' set.

For our example, we'll use another list<sup>[3](#list-3)</sup> that we think would fit into the `Flies` category, but has some variation away from the common pattern - namely including fewer `Pusgoyle Blightlords` in exchange for another unit of `Putrid Blightkings` and some `Maggoth Lord` heroes.

Again, as expected, this is correctly classified into the `Flies` archetype:
```
>>> classify(army_list = list3, bank = bank, k = 1, dist_weighted = False, war_weight = 1, enh_weight = 0)
Archetype(faction=Faction(name='Maggotkin of Nurgle'), name='Flies')
```

## Introduce a New Archetype

We may decide some unseen army lists are unique enough to warrant a new archetype, and choose to add another prototype to our knowledge bank to correctly classify them.

For our example, we'll take a variant of the `Flies` archetype that includes `Be’Lakor, the Dark Master` as well as the core of the `Flies` prototype. Arguably this is just a minor variation, but for the sake of our example we'll decide we want this to be a distinct archetype, which we'll call `Be’Lakor`.

First we can see how the existing knowledge bank classifies a list<sup>[4](#list-4)</sup> of this type:
```
>>> classify(army_list = list4, bank = bank, k = 1, dist_weighted = False, war_weight = 1, enh_weight = 0)
Archetype(faction=Faction(name='Maggotkin of Nurgle'), name='Flies')
>>>
```

Knowing this is a variant of the `Flies` archetype it makes sense that it is classified as such using the current knowledge bank.

We can set up our new archetype now:
```
>>> belakor = Archetype(faction = Faction(name = 'Maggotkin of Nurgle'), name = 'Be’Lakor')
>>>
```

### A Naive Approach

To illustrate the reasoning behind the suggestion to keep each prototype a similar size, discussed earlier when [evaluating our prototypes](#evaluate-the-prototypes), we'll start with a very small prototype and see why that does not work as expected.

Let's assume we naively decide that `Be’Lakor, the Dark Master` is the crucial component of this army list's behaviour and create a new prototype containing just that warscroll. This prototype is size `1`, compared to the sizes `5` and `6` of the other prototypes in the knowledge bank.

```
>>> naive_bank = KnowledgeBank(data = bank.data.copy())
>>> naive_belakor_proto = FlatArmyList(faction = Faction(name = 'Maggotkin of Nurgle'), warscrolls = [Warscroll(name = 'Be’Lakor, the Dark Master', count = 1)], enhancements = [])
>>> add_to_bank(archetype = belakor, army_list = naive_belakor_proto, bank = naive_bank)
```

Now we can see what happens if we try and classify our list<sup>[4](#list-4)</sup> with the new prototype present:
```
>>> classify(army_list = list4, bank = naive_bank, k = 1, dist_weighted = False, war_weight = 1, enh_weight = 0)
Archetype(faction=Faction(name='Maggotkin of Nurgle'), name='Flies')
>>>
```

It's still classified as `Flies` not `Be’Lakor` - why? Classification works by finding the army lists in the knowledge bank that are the 'closest' to the unclassified army list. The process is discussed in more detail with more complete examples [here](classification.md). A partial explanation for this example : the issue we have is the army list has `4` `Pusgoyle Blightlords` and `1` `Lord of Afflictions` in common with the `Flies` prototype, and only `1` `Be’Lakor, the Dark Master` in common with the `Be’Lakor` prototype. That means `5` votes for `Flies` and `1` vote for `Be’Lakor` in terms of similarity.

### A Better Approach

If we instead consider a `Be’Lakor` prototype that builds upon the `Flies` prototype, including every warscroll plus `Be’Lakor, the Dark Master`:
```
FlatArmyList(
    faction = Faction(name = 'Maggotkin of Nurgle'),
    warscrolls = [
        Warscroll(name = 'Be’Lakor, the Dark Master', count = 1),
        Warscroll(name = 'Lord of Afflictions', count = 1),
        Warscroll(name = 'Pusgoyle Blightlords', count = 4),
    ],
    enhancements = [],
)
```
This prototype is of size `6`, much closer to our existing prototypes of sizes `5` and `6`.

Then we add this to the knowledge bank and try classifying again:
```
>>> belakor_proto = FlatArmyList( ... paste prototype here ... )
>>> add_to_bank(archetype = belakor, army_list = belakor_proto, bank = bank)
>>> >>> classify(army_list = list4, bank = bank, k = 1, dist_weighted = False, war_weight = 1, enh_weight = 0)
Archetype(faction=Faction(name='Maggotkin of Nurgle'), name='Be’Lakor')
```

Our new list<sup>[4](#list-4)</sup> is now classified as we intended - why? Since the `Be’Lakor` prototype contains all of the warscrolls in the `Flies` prototype plus `Be’Lakor, the Dark Master`, that additional warscroll in common pushes the 'closeness' metric in favour of the `Be’Lakor` archetype. We now have `5` votes for `Flies` and `6` votes for `Be’Lakor`.

The inverse also holds, if we attempt to re-classify one of our previously classified `Flies` army lists that don't contain `Be’Lakor, the Dark Master`, they will still be classified as `Flies`. This is because even though they would have equal votes for common warscrolls, having `Be’Lakor, the Dark Master` as a dissimilar warscroll counts as a vote _against_ the closeness of the `Be’Lakor` prototype.

This example is a bit contrived, but hopefully shows the pitfalls of having dissimilarly sized prototypes, and some intuition for how to reason about the army list 'closeness' metric used in classification. Again, for more thoroughly explained examples of this metric, see [this document](classification.md).

## Next Steps

This is a very small example of only one approach for using this classifier tool.

### A Small Exercise

For any readers who are actively following the example, I've included an additional list<sup>[5](#list-5)</sup> that has been left unclassified. I encourage you to read through it, compare it to the prototypes in your knowledge bank and attempt to predict its classification, then use the tool to classify it. If you were correct, great! If not, can you reason through the process to understand why?

### Extending the Prototype Approach

An obvious extension to the example discussed here would be adding common archetypes, and their corresponding prototypes, for all of the other factions. If we limit our focus just to the competitive scene, it is reasonable to expect perhaps one to three viable archetypes for each faction at any point in the meta. This means manual creation and maintenance of the knowledge bank is actually a reasonable endeavour.

With a classifier set up like this, tournament lists could be automatically fed through to determine their archetypes, with that classification used to label their results. Then, win rates and other statistics could be broken down by army list archetype rather than by faction, giving a more transparent view of the metagame and how it shifts.

### A Big Data Approach

An alternative approach to classification would be using a large number of raw army lists in the knowledge bank. This could mean a classifier setup using a higher value of 'k' and a knowledge bank containing every army list classified, and is supported by the tool as well.

The initial knowledge bank would likely have to be larger, and so take more effort to label every data point with an archetype, but would require no decision making regarding creating army list prototypes. Arguably prototypes are yet another configurable (and complex) parameter to tune, so removing that step may be appealing, especially for a more automated approach.

Then, newly classified army lists can be added straight to the knowledge bank with their assigned archetype, and the data set gets bigger and potentially better at classifying future data with each new classification performed.

Given that the knowledge bank continually grows, data pruning is probably prudent with this approach, which is discussed to some extent [here](classification.md). There are algorithms for performing pruning, or it can be done manually, with the goal being to maintain (or even improve) classification accuracy with some subset of the total data set.

### Use as a Building Block

I've alluded to some uses for classification that I think are cool, but the classifier tool could easily be included in other projects to serve a variety of purposes. As a more metaphorical building block, the classification approach here could also be treated as a proof of concept, and inspire new and better approaches perhaps using other areas of statistics or machine learning. Both of which I highly encourage.

To either end, the algorithms and data structures used by this tool are very simple and don't rely on libraries that put any behaviour in a 'black box', with the intent that a reader can quickly understand the inner workings of the tool and use it to further their own projects, in whichever language or framework they prefer.


## Appendix

### List 1
#### Colin Klaren

```
Allegiance: Maggotkin of Nurgle
– Subfaction: Filthbringers
– Grand Strategy: Take What’s Theirs
– Triumphs: Inspired

Leaders
Rot Coven Rotbringer Sorcerer (120)*
– General
– Command Trait: Master of Magic
– Artefact: Arcane Tome (Universal Artefact)
– Lore of Malignance: Rancid Visitations
– Lore of Malignance: Gift of Disease
Rot Coven Rotbringer Sorcerer (120)*
– Lore of Malignance: Rancid Visitations
– Lore of Malignance: Cloying Quagmire
Rot Coven Rotbringer Sorcerer (120)*
– Lore of Malignance: Blades of Putrefaction
– Lore of Malignance: Magnificent Buboes

Battleline
10 x Putrid Blightkings (500)**
– Reinforced x 1
5 x Putrid Blightkings (250)**
10 x Plaguebearers (150)**
2 x Pusgoyle Blightlords (220)***
– 1x Dolorous Tocsin
2 x Pusgoyle Blightlords (220)***
– 1x Dolorous Tocsin

Units
3 x Nurglings (105)*

Endless Spells & Invocations
Umbral Spellportal (70)
Ravenak’s Gnashing Jaws (60)
Shards of Valagharr (50)

Core Battalions
*Warlord
**Expert Conquerors
***Bounty Hunters

Additional Enhancements
Spell

Total: 1985 / 2000
Reinforced Units: 1 / 4
Allies: 0 / 400
Wounds: 142
```

### List 2
#### Christian Riel

```
Allegiance: Maggotkin of Nurgle
– Subfaction: Drowned Men
– Mortal Realm: Ghyran
– Grand Strategy: Take What’s Theirs
– Triumphs:

Leaders
Festus the Leechlord (150)**
– Lore of Malignance: Rancid Visitations
Lord of Afflictions (210)**
– General
– Command Trait: Overpowering Stench
– Artefact: The Splithorn Helm
Lord of Blights (150)**

Battleline
4 x Pusgoyle Blightlords (440)*
– 2x Dolorous Tocsin
– Reinforced x 1
2 x Pusgoyle Blightlords (220)*
– 1x Dolorous Tocsin
2 x Pusgoyle Blightlords (220)*
– 1x Dolorous Tocsin
10 x Putrid Blightkings (500)**
– Reinforced x 1

Units
1 x Pusgoyle Blightlords – Single (110)**

Core Battalions
*Bounty Hunters
**Battle Regiment

Total: 2000 / 2000
Reinforced Units: 2 / 4
Allies: 0 / 400
Wounds: 132
Drops: 4
```

### List 3
#### Marco D'Anna

```
Allegiance: Maggotkin of Nurgle
– Subfaction: Drowned Men
– Mortal Realm: Ghur
– Grand Strategy: Show of Dominance
– Triumphs: Inspired

Leaders
Lord of Afflictions (210)*
– General
– Command Trait: Overpowering Stench
– Artefact: The Splithorn Helm
Orghotts Daemonspew (300)*
Bloab Rotspawned (300)
– Lore of Malignance: Gift of Disease

Battleline
10 x Putrid Blightkings (500)**
5 x Putrid Blightkings (250)**
2 x Pusgoyle Blightlords (220)*
– 1 x Dolorous Tocsin
2 x Pusgoyle Blightlords (220)*
– 1 x Dolorous Tocsin

Core Battalions
*Battle Regiment
**Expert Conquerors

Total: 2000/2000
Wounds: 127
Allies: 0/400
Reinforced Units: 1/4
Drops: 4
```

### List 4
#### Hadrien Torrin

```
Allegiance: Maggotkin of Nurgle
– Subfaction: Drowned Men
– Grand Strategy: Blessed Desecration
– Triumphs: Inspired

Leaders
Be’Lakor, the Dark Master (360)*
– Allies
Lord of Afflictions (210)*
– General
– Command Trait: Overpowering Stench
– Artefact: The Splithorn Helm
– Dolorous Tocsin
– Incubatch

Battleline
4 x Pusgoyle Blightlords (440)*
– 2x Dolorous Tocsin
– Reinforced x 1
4 x Pusgoyle Blightlords (440)*
– 2x Dolorous Tocsin
– Reinforced x 1
2 x Pusgoyle Blightlords (220)*
– 1x Dolorous Tocsin
2 x Pusgoyle Blightlords (220)*
– 1x Dolorous Tocsin

Units
3 x Nurglings (105)*

Core Battalions
*Battle Regiment

Total: 1995 / 2000
Reinforced Units: 2 / 4
Allies: 360 / 400
Wounds: 130
Drops: 1
```

### List 5
#### Tobias Kempf

```
Allegiance: Maggotkin of Nurgle
– Subfaction: Drowned Men
– Grand Strategy: No Place for the Weak
– Triumphs: Bloodthirsty

Leaders
Be’Lakor, the Dark Master (360)*
– Allies
Lord of Afflictions (210)*
– General
– Command Trait: Overpowering Stench
– Artefact: Arcane Tome (Universal Artefact)
– Lore of Malignance: Rancid Visitations

Battleline
10 x Plaguebearers (150)*
2 x Pusgoyle Blightlords (220)*
– 1x Dolorous Tocsin
4 x Pusgoyle Blightlords (440)*
– 2x Dolorous Tocsin
– Reinforced x 1
4 x Pusgoyle Blightlords (440)*
– 2x Dolorous Tocsin
– Reinforced x 1

Units
3 x Nurglings (105)*

Endless Spells & Invocations
Ravenak’s Gnashing Jaws (60)

Core Battalions
*Battle Regiment

Total: 1985 / 2000
Reinforced Units: 2 / 4
Allies: 360 / 400
Wounds: 134
Drops: 1
```
