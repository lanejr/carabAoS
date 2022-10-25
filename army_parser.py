import unittest
import itertools
from army_flattener import *
from parsec import *

# TODO: parsers
# parser rules:
# Faction - anything starting 'Allegiance: '
# Warscroll - beneath 'Leaders', 'Battleline', etc; anything _not_ starting '- '
# Enhancement - beneath 'Leaders', 'Battleline', etc; anything starting '- [a-z]*: '

@dataclass
class ParsedAllegiance:
    """
    A class representing a parsed allegiance and its features.

    An intermediary representation before further processing.
    """

    name: str
    features: list[str]

@dataclass
class ParsedWarscroll:
    """
    A class representing a parsed warscroll and its enhancements.

    An intermediary representation before further processing.
    """

    name: str
    enhancements: list[str]

rest_of_line: Parser = regex('[^\r\n]+')
whitespace: Parser = regex('[^\S\r\n]+')
new_line: Parser = regex('\r?\n')
bullet: Parser = string("- ")

@generate
def parse_faction():
    # parse the name of the allegiance
    prefix: Parser = string("Allegiance: ")
    name = yield whitespace >> prefix >> rest_of_line << new_line

    # parse any listed features
    prefix: Parser = whitespace + bullet
    features = yield sepBy(prefix >> rest_of_line, new_line)

    return ParsedAllegiance(name, features)

@generate
def parse_warscrolls():
    # TODO: do more here? some conversion?
    warscrolls = yield many(section)
    return list(itertools.chain(*warscrolls))

@generate
def header():
    # parse any known header
    header = yield\
        string("Leaders") ^\
        string("Battleline") ^\
        string("Units") ^\
        string("Behemoths") ^\
        string("Artillery") ^\
        string("Spells")
    return header

@generate
def section():
    # parse the section header
    section_header = yield spaces() >> header << new_line

    # parse the listed warscroll(s)
    warscrolls = yield many1(warscroll)
    return warscrolls

@generate
def warscroll():
    # parse the name of the warscroll
    name = yield whitespace >> rest_of_line << new_line

    # parse any listed enhancements
    prefix: Parser = whitespace + bullet
    enhancements = yield sepBy(prefix >> rest_of_line, new_line)

    return ParsedWarscroll(name, enhancements)

class TestArmyParser(unittest.TestCase):

    def test_parse_faction(self) -> None:
        input_str: str = """\
            Allegiance: Ogor Mawtribes
            - Mawtribe: Bloodgullet
            - Grand Strategy: Beast Master
            - Triumphs: Inspired
        """

        expected: ParsedAllegiance = ParsedAllegiance(
            name="Ogor Mawtribes",
            features=[
                "Mawtribe: Bloodgullet",
                "Grand Strategy: Beast Master",
                "Triumphs: Inspired",
            ]
        )
        result: ParsedAllegiance = parse_faction.parse(input_str)

        self.assertEqual(result, expected)

    def test_parse_warscrolls(self) -> None:
        input_str: str = """\
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
        """

        expected: list[ParsedWarscroll] = [
            ParsedWarscroll("Kragnos, The End of Empires (720)", []),
            ParsedWarscroll(
                name = "Frostlord on Stonehorn (430)",
                enhancements = [
                    "General",
                    "Command Trait: Nice Drop of the Red Stuff!",
                    "Artefact: Splatter-cleaver",
                    "Mount Trait: Metalcruncher",
                ],
            ),
            ParsedWarscroll(
                name = "Huskard on Stonehorn (340)*",
                enhancements = ["Blood Vulture"],
            ),
            ParsedWarscroll(
                name = "2 x Mournfang Pack (160)*",
                enhancements = ["Gargant Hackers"],
            ),
            ParsedWarscroll(
                name = "2 x Mournfang Pack (160)*",
                enhancements = ["Gargant Hackers"],
            ),
            ParsedWarscroll(
                name = "2 x Mournfang Pack (160)*",
                enhancements = ["Gargant Hackers"],
            ),
        ]
        result = parse_warscrolls.parse(input_str)

        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()