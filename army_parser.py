import unittest
from army_flattener import *
from parsec import *

# TODO: parsers
# parser rules:
# Faction - anything starting 'Allegiance: '
# Warscroll - beneath 'Leaders', 'Battleline', etc; anything _not_ starting '- '
# Enhancement - beneath 'Leaders', 'Battleline', etc; anything starting '- [a-z]*: '

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


def parse_faction(input: str) -> Faction:
    prefix: Parser = string("Allegiance: ")
    parser: Parser = spaces() >> prefix >> rest_of_line << spaces()
    parsed: str = parser.parse(input)
    return Faction(parsed)

@generate
def parse_warscrolls():
    # TODO: do more here? some conversion?
    warscrolls = yield many(section)
    return warscrolls 

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
    prefix: Parser = whitespace + string("- ")
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
        result: Faction = parse_faction(input_str)
        expected: Faction = Faction("Ogor Mawtribes")
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

        parser = parse_warscrolls
        parsed = parser.parse(input_str)
        print("finished")
        print(parsed)

        #result = parse_warscrolls(input_str)
        expected: list[Warscroll] = [
            Warscroll("Kragnos, The End of Empires", 1),
            Warscroll("Frostlord on Stonehorn", 1),
            Warscroll("Huskard on Stonehorn", 1),
            Warscroll("Mournfang Pack", 3),
        ]
        #self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()