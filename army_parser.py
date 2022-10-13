import unittest
from army_flattener import *
from parsec import *

# TODO: parsers
# parser rules:
# Faction - anything starting 'Allegiance: '
# Warscroll - beneath 'Leaders', 'Battleline', etc; anything _not_ starting '- '
# Enhancement - beneath 'Leaders', 'Battleline', etc; anything starting '- [a-z]*: '

end_of_line: Parser = many(none_of('\n'))

def parse_faction(input: str) -> Faction:
    prefix: Parser = string("Allegiance: ")
    parser: Parser = spaces() >> prefix >> end_of_line << spaces()
    parsed: str = "".join(parser.parse(input))
    return Faction(parsed)

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

if __name__ == '__main__':
    unittest.main()