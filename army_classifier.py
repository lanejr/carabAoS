from dataclasses import dataclass
from army_flattener import *
import unittest

### Data classes ###

@dataclass(frozen = True)
class Archetype:
    """
    A class representing an army list archetype.

    Common archetypes exist within factions, with a core set of warscrolls and
    enhancements that define the essence of how the army plays, and small
    deviations between different players' interpretations.
    """

    faction: Faction
    name: str

@dataclass(frozen = False)
class KnowledgeBank:
    """
    A class representing a set of army lists labelled with their archetypes.

    For classification of unseen army lists within an archetype, a good set of
    pre-classified army lists are required. This can be viewed as the knowledge
    bank of the machine learning algorithm.

    To initialise the learning this data would need to be manually labelled,
    but subsequent data labelled by the algorithm can also be added to the data
    set to grow its knowledge bank. Occasional manual updates may be necessary
    when new archetypes are created, or to prune mislabelled data.
    """

    data: dict[Archetype, list[FlatArmyList]]


### Public ###

# TODO: obvious usages:
# build a knowledge bank from raw lists, (done)
# classify a raw list, 
# add newly classified list back into knowledge bank, (done?)
# import / export knowledge banks?

def classify(army_list: FlatArmyList, bank: KnowledgeBank):
    """
    Classify an army list into a particular archetype using a knowledge bank.

    The labelled army list is not added to the knowledge bank.

    k-nearest neighbours is used for classification, with proximity
    defined using the Levenshtein distance between two army lists.
    """

    # TODO
    pass

def add_to_bank(
    archetype: Archetype,
    army_list: FlatArmyList,
    bank: KnowledgeBank = KnowledgeBank({}),
) -> KnowledgeBank:
    """
    Add an army list labelled with its archetype into a knowledge bank.

    This modifies the passed knowledge bank, and also returns it for
    convenience. If no knowledge bank is provided, a new one is first created.
    """

    assert archetype.faction == army_list.faction

    # insert the army list into the knowledge bank, under its archetype
    bank.data.setdefault(archetype, []).append(army_list)

    # return the modified knowledge bank
    return bank

### Tests ###

class __TestArmyClassifier(unittest.TestCase):

    def test_add_to_bank(self) -> None:
        faction: Faction = Faction("Ogor Mawtribes")

        # Add an army of one archetype
        archetype_1: Archetype = Archetype(
            faction = faction,
            name = "Kragnos Beastclaw Raiders"
        )
        army_list_1: FlatArmyList = FlatArmyList(
            faction = faction,
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
        bank: KnowledgeBank = add_to_bank(
            archetype = archetype_1,
            army_list = army_list_1,
        )

        # Add an army of a second archetype but the same faction
        archetype_2: Archetype = Archetype(
            faction = faction,
            name = "Incarnate Beastclaw Raiders"
        )
        army_list_2: FlatArmyList = FlatArmyList(
            faction = faction,
            warscrolls = [
                Warscroll('Frostlord on Stonehorn', 1),
                Warscroll('Slaughtermaster', 1),
                Warscroll('Mournfang Pack', 2),
                Warscroll('Stonehorn Beastriders', 2),
                Warscroll('Frost Sabres', 1),
                Warscroll('Krondspine Incarnate of Ghur', 1)
            ], 
            enhancements = [
                Enhancement('Nice Drop of the Red Stuff!', 1),
                Enhancement('Splatter-cleaver', 1),
                Enhancement('Metalcruncher', 1),
                Enhancement('Molten Entrails', 1),
                Enhancement('Ribcracker', 1),
            ],
        )
        add_to_bank(
            archetype = archetype_2,
            army_list = army_list_2,
            bank = bank,
        )

        # Add another army of the first archetype
        army_list_3: FlatArmyList = FlatArmyList(
            faction = faction,
            warscrolls = [
                Warscroll("Kragnos, The End of Empires", 1),
                Warscroll("Frostlord on Stonehorn", 1),
                Warscroll('Stonehorn Beastriders', 2),
                Warscroll("Mournfang Pack", 1),
            ],
            enhancements = [
                Enhancement("Nice Drop of the Red Stuff!", 1),
                Enhancement("Splatter-cleaver", 1),
                Enhancement("Metalcruncher", 1),
            ],
        )
        add_to_bank(
            archetype = archetype_1,
            army_list = army_list_3,
            bank = bank,
        )

        self.assertEqual(bank.data[archetype_1], [army_list_1, army_list_3])
        self.assertEqual(bank.data[archetype_2], [army_list_2])


if __name__ == '__main__':
    unittest.main()