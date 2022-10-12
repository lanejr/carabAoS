from dataclasses import dataclass
import unittest
import parsec

Faction = str

@dataclass
class Warscroll:
    """ 
    A class representing a warscroll and its number of occurrences.

    Occurrences are counted both by the number of times a warscroll appears in
    an army list and the number of times it is reinforced.
    """

    name: str
    count: int

@dataclass
class Enhancement:
    """
    A class representing an enhancement and its number of occurrences.

    Only enhancements applied to warscrolls should qualify - i.e. command 
    traits, artefacts, spells, prayers, and mount traits, and not triumphs.
    """

    name: str
    count: int

@dataclass
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

def flatten(army_list: str) -> FlatArmyList:
    # TODO: get these properly
    faction: Faction = ""
    warscrolls: list[Warscroll] = []
    enhancements: list[Enhancement] = []

    flat_list = FlatArmyList(faction, warscrolls, enhancements)
    return flat_list

# TODO: parsers
# parser rules:
# Faction - anything starting 'Allegiance: '
# Warscroll - beneath 'Leaders', 'Battleline', etc; anything _not_ starting '- '
# Enhancement - beneath 'Leaders', 'Battleline', etc; anything starting '- [a-z]*: '

def parse_faction(x: str) -> Faction:
    parser = parsec.spaces() >> parsec.string("Allegiance: ") >> parsec.many(parsec.none_of('\n')) << parsec.spaces()
    parsed: str = "".join(parser.parse(x))
    return Faction(parsed)

class TestWarscrollParser(unittest.TestCase):

    def test_parse_faction(self):
        input_str: str = """\
            Allegiance: Ogor Mawtribes
        """
        result = parse_faction(input_str)
        expected = Faction("Ogor Mawtribes")
        self.assertEqual(result, expected)

    def test_parse(self):
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

        faction: Faction = "Ogor Mawtribes"

        warscrolls: list[Warscroll] = [
            Warscroll("Kragnos, The End of Empires", 1),
            Warscroll("Frostlord on Stonehorn", 1),
            Warscroll("Huskard on Stonehorn", 1),
            Warscroll("Mournfang Pack", 3),
        ]

        enhancements: list[Enhancement] = [
            Enhancement("Nice Drop of the Red Stuff!", 1),
            Enhancement("Splatter-cleaver", 1),
            Enhancement("Metalcruncher", 1),
        ]
    
    # TODO: test reinforced units



if __name__ == '__main__':
    unittest.main()
