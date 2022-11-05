from dataclasses import dataclass
import unittest
import itertools
from parsec import *

### Data classes ###

@dataclass(frozen = True)
class ParsedAllegiance:
    """
    A class representing a parsed allegiance and its features.

    An intermediary representation before further processing.
    """

    name: str
    features: list[str]

@dataclass(frozen = True)
class ParsedWarscroll:
    """
    A class representing a parsed warscroll and its features.

    An intermediary representation before further processing.
    """

    name: str
    features: list[str]


### Parsers ###

# parse to the end of the line
_rest_of_line: Parser = regex('[^\r\n]+')

# parse all non line ending whitespace
_whitespace: Parser = regex('[^\S\r\n]*')

# parse a new line
_new_line: Parser = regex('\r?\n')

# parse a bullet point (or its similar but easily confused alternative)
_bullet: Parser = string("- ") ^ string("– ")


### Public ###

@generate
def list_str():
    """
    Parse an army list into parsed allegiance and warscrolls data classes.

    Only works for army lists following the format used in the warhammer
    community warscroll builder tool.
    """

    parsed_allegiance = yield _allegiance
    parsed_warscrolls = yield _warscrolls
    return (parsed_allegiance, parsed_warscrolls)

@generate
def enhancement():
    """
    Parse an enhancement string, stripping its prefix.

    Extracts command traits, artefacts, prayers and mount traits only.
    """

    # either parse a prefixed enhancement, or consume the line and discard it
    prefix: Parser = regex('[\w\s]+: ')
    name = yield (prefix >> _rest_of_line) | result(_rest_of_line, None)
    return name

@generate
def reinforcement():
    """
    Parse a reinforcement count.

    Extracts just the number of reinforcements.
    """

    # either parse a reinforcement count, or consume the line and discard it
    prefix: Parser = string("Reinforced x ")
    count = yield (prefix >> digit()) | result(_rest_of_line, None)
    return count


### Private ###

@generate
def _allegiance():
    # parse the name of the allegiance
    prefix: Parser = string("Allegiance: ")
    name = yield _whitespace >> prefix >> _rest_of_line << _new_line

    # parse any listed features
    prefix: Parser = _whitespace + _bullet
    features = yield sepBy(prefix >> _rest_of_line, _new_line)

    return ParsedAllegiance(name, features)

@generate
def _warscrolls():
    # parse each section for warscrolls
    warscrolls = yield many(_section)

    # flatten the nested warscrolls into a single list
    return list(itertools.chain(*warscrolls))

@generate
def _header():
    # parse any known header
    header = yield\
        string("Leaders") ^\
        string("Battleline") ^\
        string("Units") ^\
        string("Behemoths") ^\
        string("Artillery") ^\
        string("Endless Spells & Invocations")
    return header

@generate
def _section():
    # sections are usually separated by new lines
    yield many(_new_line)

    # parse the section header
    section_header = yield _whitespace >> _header << _new_line

    # parse the listed warscroll(s)
    warscrolls = yield many1(_warscroll)
    return warscrolls

@generate
def _warscroll():
    # parse the name of the warscroll
    count: Parser = regex('(\d+ x )?')
    to_end: Parser = regex('[^\(\r\n]+')
    name = yield _whitespace >> count >> to_end << _rest_of_line << _new_line

    # drop the trailing space
    name = name[:len(name) - 1]

    # parse any listed features
    prefix: Parser = _whitespace + _bullet
    features = yield sepBy(prefix >> _rest_of_line, _new_line)

    return ParsedWarscroll(name, features)


### Tests ###

class __TestArmyParser(unittest.TestCase):

    def test_parse_list_str(self) -> None:
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

        allegiance: ParsedAllegiance = ParsedAllegiance(
            name="Ogor Mawtribes",
            features=[
                "Mawtribe: Bloodgullet",
                "Grand Strategy: Beast Master",
                "Triumphs: Inspired",
            ]
        )

        warscrolls: list[ParsedWarscroll] = [
            ParsedWarscroll("Kragnos, The End of Empires", []),
            ParsedWarscroll(
                name = "Frostlord on Stonehorn",
                features = [
                    "General",
                    "Command Trait: Nice Drop of the Red Stuff!",
                    "Artefact: Splatter-cleaver",
                    "Mount Trait: Metalcruncher",
                ],
            ),
            ParsedWarscroll(
                name = "Huskard on Stonehorn",
                features = ["Blood Vulture"],
            ),
            ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
            ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
            ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
        ]

        expected: tuple[ParsedAllegiance, list[ParsedWarscroll]] = (
            allegiance, 
            warscrolls,
        )
        result = list_str.parse(input_str)

        self.assertEqual(result, expected)
    
    def test_parse_enhancement(self) -> None:
        self.assertEqual(enhancement.parse("General"), None)
        self.assertEqual(
            enhancement.parse("Command Trait: Nice Drop of the Red Stuff!"),
            "Nice Drop of the Red Stuff!",
        )
        self.assertEqual(
            enhancement.parse("Artefact: Splatter-cleaver"),
            "Splatter-cleaver",
        )
        self.assertEqual(
            enhancement.parse("Mount Trait: Metalcruncher"),
            "Metalcruncher"
        )
    
    def test_parse_reinforcement(self) -> None:
        self.assertEqual(reinforcement.parse("Gargant Hackers"), None)
        self.assertEqual(reinforcement.parse("Reinforced x 1"), '1')
        self.assertEqual(reinforcement.parse("Reinforced x 2"), '2')
    
    def test_parse_allegiance(self) -> None:
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
        result: ParsedAllegiance = _allegiance.parse(input_str)

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
            ParsedWarscroll("Kragnos, The End of Empires", []),
            ParsedWarscroll(
                name = "Frostlord on Stonehorn",
                features = [
                    "General",
                    "Command Trait: Nice Drop of the Red Stuff!",
                    "Artefact: Splatter-cleaver",
                    "Mount Trait: Metalcruncher",
                ],
            ),
            ParsedWarscroll(
                name = "Huskard on Stonehorn",
                features = ["Blood Vulture"],
            ),
            ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
            ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
            ParsedWarscroll(
                name = "Mournfang Pack",
                features = ["Gargant Hackers"],
            ),
        ]
        result: list[ParsedWarscroll] = _warscrolls.parse(input_str)

        self.assertEqual(result, expected)
    

if __name__ == '__main__':
    unittest.main()