# How to Flatten an Army List

This document will loosely guide a user through one method of flattening an army list with the `army_flattener` tool. We will flatten a simple Ogor Mawtribes list as a worked example.

## Copy the Army List Text

The first step will be grabbing an army list to flatten. The tool currently supports army lists exported from the warhammer community [warscroll builder](https://www.warhammer-community.com/warscroll-builder/), so we'll build our list using that and export the text.

For example:
```
Allegiance: Ogor Mawtribes
- Mawtribe: Bloodgullet
- Grand Strategy: Beast Master
- Triumphs: Inspired

Leaders
Kragnos, The End of Empires (720)
Frostlord on Stonehorn (430)
- General
- Command Trait: Nice Drop of the Red Stuff!
- Artefact: Splatter-cleaver
- Mount Trait: Metalcruncher
Huskard on Stonehorn (340)*
- Blood Vulture

Battleline
2 x Mournfang Pack (160)*
- Gargant Hackers
2 x Mournfang Pack (160)*
- Gargant Hackers
2 x Mournfang Pack (160)*
- Gargant Hackers

Core Battalions
*Battle Regiment

Total: 1970 / 2000
Reinforced Units: 0 / 4
Allies: 0 / 400
Wounds: 79
Drops: 3 
```

## Open the Python Interpreter

For this guide we'll just use the Python interpreter to call our `flatten` function. 

We should make sure we have any required modules installed, using `pip` and the `requirements.txt` file in the project.

```
$ pip3 install -r requirements.txt
```

Next we can open the interpreter in the `src/` directory:

```
$ cd src/
$ python3
```

## Input the Army List

Let's assign our army list to a `str` variable, we should first type the following (but not hit enter yet!):

```
>>> army_list = """
```

Now we can paste the army list string into the interpreter, and close the statement (now we should hit enter):

```
... Wounds: 79
... Drops: 3 """
>>>
```

To double check the army list looks ok we can print our variable:

```
>>> print(army_list)
```

This should appear exactly as we copied it from the warscroll builder tool.

## Flatten the Army List

Now we should import our `flatten` function:

```
>>> from army_flattener import flatten
>>>
```

And we can call this function to flatten our army list, saving the result to a new variable:

```
>>> flat_army_list = flatten(army_list)
>>>
```

As before, to see the result we can print our new variable:

```
>>> print(flat_army_list)
FlatArmyList(faction=Faction(name='Ogor Mawtribes'), warscrolls=[Warscroll(name='Kragnos, The End of Empires', count=1), Warscroll(name='Frostlord on Stonehorn', count=1), Warscroll(name='Huskard on Stonehorn', count=1), Warscroll(name='Mournfang Pack', count=3)], enhancements=[Enhancement(name='Nice Drop of the Red Stuff!', count=1), Enhancement(name='Splatter-cleaver', count=1), Enhancement(name='Metalcruncher', count=1)])
>>>
```

As an aside, to see data like this in a more human-readable way we can instead 'pretty print' like so:

```
>>> from pprint import pprint
>>> pprint(flat_army_list)
FlatArmyList(faction=Faction(name='Ogor Mawtribes'),
    warscrolls=[Warscroll(name='Kragnos, The End of Empires', count=1),
                Warscroll(name='Frostlord on Stonehorn', count=1),
                Warscroll(name='Huskard on Stonehorn', count=1),
                Warscroll(name='Mournfang Pack', count=3)],
    enhancements=[Enhancement(name='Nice Drop of the Red Stuff!', 
                              count=1),
                  Enhancement(name='Splatter-cleaver', count=1),
                  Enhancement(name='Metalcruncher', count=1)])
>>>
```

## Next Steps

I would expect in most cases flattening an army list is a means to an end, not the goal in and of itself. In this toolbox flattened army lists are used for army list classification, but there are many other possible uses which I encourage the reader to consider and explore!
