from abc import ABCMeta
from dataclasses import dataclass
import army_parser as parser
import unittest

### Data classes ###

@dataclass(frozen = True)
class Faction:
    """
    A class representing the faction of the army list.

    The word 'faction' is used to be mean the level above 'subfaction' - e.g.
    Ironjawz would be a faction, the level above subfactions like Bloodtoofs,
    and in this case the level beneath the battletome Orruk Warclans.
    """

    name: str

@dataclass(frozen = True, order = True)
class Item(metaclass = ABCMeta):
    """
    An abstract base class representing a generic army list item.

    Each item has a name and a count of its occurrences in an army list.
    """

    name: str
    count: int

@dataclass(frozen = True, order = True)
class Warscroll(Item):
    """ 
    A class representing a warscroll and its number of occurrences.

    Occurrences are counted both by the number of times a warscroll appears in
    an army list and the number of times it is reinforced.
    """

@dataclass(frozen = True, order = True)
class Enhancement(Item):
    """
    A class representing an enhancement and its number of occurrences.

    Only enhancements applied to warscrolls should qualify - i.e. command 
    traits, artefacts, spells, prayers, and mount traits, and not triumphs.
    """

@dataclass(frozen = True)
class FlatArmyList:
    """
    A class representing a 'flattened' army list.

    The core essence of an army list created by 'flattening' the structure
    into the faction and two (metaphorical) decks of cards - warscrolls and 
    enhancements.
    """

    faction: Faction
    warscrolls: list[Warscroll]
    enhancements: list[Enhancement]


### Public ###

def flatten(army_list: str) -> FlatArmyList:
    """
    Parse an army list string into a flattened army list data class.

    Only works for army lists following the format used in the warhammer
    community warscroll builder tool.
    """
    (parsed_allegiance, parsed_warscrolls) = parser.list_str.parse(army_list)

    faction: Faction = Faction(name = parsed_allegiance.name)
    wars: list[Warscroll] = _convert_warscrolls(parsed_warscrolls)
    enhs: list[Enhancement] = _convert_enhancements(parsed_warscrolls)

    return FlatArmyList(faction, wars, enhs)


### Private ###

def _convert_enhancements(
    warscrolls: list[parser.ParsedWarscroll]
) -> list[Enhancement]:
    parsed_enhs: dict[str, int] = {}

    # iterate over all features in warscrolls
    for warscroll in warscrolls:
        for feature in warscroll.features:

            # parse the enhancement name if it is valid
            parsed_enh = parser.enhancement.parse(feature)
            if parsed_enh != None:

                # keep a count of valid enhancements
                count: int = parsed_enhs.setdefault(parsed_enh, 0)
                parsed_enhs[parsed_enh] = count + 1

    # convert counted enhancements into data classes
    return [Enhancement(name, count) for name, count in parsed_enhs.items()]

def _convert_warscrolls(
    warscrolls: list[parser.ParsedWarscroll]
) -> list[Warscroll]:
    parsed_wars: dict[str, int] = {}

    # iterate over all warscrolls
    for warscroll in warscrolls:
        name: str = warscroll.name
        to_add: int = 1

        # check features for reinforcement, and note how many times
        for feature in warscroll.features:
            reinf = parser.reinforcement.parse(feature)
            if reinf != None:
                to_add: int = to_add + int(reinf)

        # keep a count of warscroll occurrences (including reinforcements)
        count: int = parsed_wars.setdefault(name, 0)
        parsed_wars[name] = count + to_add
    
    # convert counted warscrolls into data classes
    return [Warscroll(name, count) for name, count in parsed_wars.items()]


### Tests ###

class __TestArmyFlattener(unittest.TestCase):

    def test_flatten(self) -> None:
        input_str: str = """\
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
        """

        expected: FlatArmyList = FlatArmyList(
            faction = Faction("Ogor Mawtribes"),
            warscrolls = [
                Warscroll("Kragnos, The End of Empires", 1),
                Warscroll("Frostlord on Stonehorn", 1),
                Warscroll("Huskard on Stonehorn", 1),
                Warscroll("Mournfang Pack", 3),
            ],
            enhancements = [
                Enhancement("Nice Drop of the Red Stuff!", 1),
                Enhancement("Splatter-cleaver", 1),
                Enhancement("Metalcruncher", 1),
            ],
        )
        result: FlatArmyList = flatten(input_str)

        self.assertEqual(result, expected)

    def test_convert_enhancements(self) -> None:
        warscrolls: list[parser.ParsedWarscroll] = [
            parser.ParsedWarscroll("Kragnos, The End of Empires", []),
            parser.ParsedWarscroll(
                name = "Frostlord on Stonehorn",
                features = [
                    "General",
                    "Command Trait: Nice Drop of the Red Stuff!",
                    "Artefact: Splatter-cleaver",
                    "Mount Trait: Metalcruncher",
                ],
            ),
            parser.ParsedWarscroll(
                name = "Huskard on Stonehorn",
                features = ["Blood Vulture"],
            ),
            parser.ParsedWarscroll(
                name = "Butcher",
                features = [
                    "Lore of Gutmagic: Ribcracker",
                    "Bloodgullet 2nd Spell: Molten Entrails"
                ],
            ),
            parser.ParsedWarscroll(
                name = "Butcher",
                features = [
                    "Lore of Gutmagic: Greasy Deluge",
                    "Bloodgullet 2nd Spell: Ribcracker"
                ],
            ),
            parser.ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
            parser.ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
            parser.ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
        ]

        expected: list[Enhancement] = [
            Enhancement("Nice Drop of the Red Stuff!", 1),
            Enhancement("Splatter-cleaver", 1),
            Enhancement("Metalcruncher", 1),
            Enhancement("Ribcracker", 2),
            Enhancement("Molten Entrails", 1),
            Enhancement("Greasy Deluge", 1),
        ]
        result: list[Enhancement] = _convert_enhancements(warscrolls)

        self.assertEqual(result, expected)

    def test_convert_warscrolls(self) -> None:
        warscrolls: list[parser.ParsedWarscroll] = [
            parser.ParsedWarscroll("Kragnos, The End of Empires", []),
            parser.ParsedWarscroll(
                name = "Frostlord on Stonehorn",
                features = [
                    "General",
                    "Command Trait: Nice Drop of the Red Stuff!",
                    "Artefact: Splatter-cleaver",
                    "Mount Trait: Metalcruncher",
                ],
            ),
            parser.ParsedWarscroll(
                name = "Huskard on Stonehorn",
                features = ["Blood Vulture"],
            ),
            parser.ParsedWarscroll(
                name = "Mournfang Pack",
                features = [
                    "Gargant Hackers",
                    "Reinforced x 1"
                ],
            ),
            parser.ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
        ]

        expected: list[Warscroll] = [
            Warscroll("Kragnos, The End of Empires", 1),
            Warscroll("Frostlord on Stonehorn", 1),
            Warscroll("Huskard on Stonehorn", 1),
            Warscroll("Mournfang Pack", 3),
        ]
        result: list[Warscroll] = _convert_warscrolls(warscrolls)

        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
