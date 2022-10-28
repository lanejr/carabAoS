from dataclasses import dataclass
from typing import TypeVar
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

def classify(
    army_list: FlatArmyList,
    bank: KnowledgeBank,
    k: int = 1,
):
    """
    Classify an army list into a particular archetype using a knowledge bank.

    If no archetypes of the same faction as the passed army list exist in the
    knowledge bank 'None' is returned.

    The labelled army list is not added to the knowledge bank.

    k-nearest neighbours is used for classification, with proximity
    defined using the Levenshtein distance between two army lists.
    """

    faction: Faction = army_list.faction
    dists = {}
    for archetype, army_lists in bank.data.items():
        # look only at archetypes of the same faction
        if archetype.faction == faction:
            # get distances to each army list in the archetype
            dists[archetype] = [_distance(army_list, a_l) for a_l in army_lists]
    
    # TODO: find the smallest k dists, and their archetypes, then assign highest count

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

    # sort the warscrolls and enhancements for easier comparison later
    army_list.warscrolls.sort()
    army_list.enhancements.sort()

    # insert the army list into the knowledge bank, under its archetype
    bank.data.setdefault(archetype, []).append(army_list)

    # return the modified knowledge bank
    return bank

def _distance(
    army_list_1: FlatArmyList,
    army_list_2: FlatArmyList,
    war_weight: int = 1,
    enh_weight: int = 1,
) -> int:
    """
    Calculate the levenshtein distance between two army lists.

    Pre-condition: both army lists' warscrolls and enhancements are sorted.

    Warscroll and enhancement distances can optionally be weighted differently.
    """
    war_dist: int = _lev_distance(
        army_list_1.warscrolls, 
        army_list_2.warscrolls,
    )

    enh_dist: int = _lev_distance(
        army_list_1.enhancements, 
        army_list_2.enhancements,
    )

    return war_dist * war_weight + enh_dist * enh_weight

I = TypeVar("I", bound = Item)
def _lev_distance(list_1: list[I], list_2: list[I]) -> int:

    len_1: int = len(list_1) + 1
    len_2: int = len(list_2) + 1

    # initialise distance matrix to 0
    # use a list to represent matrix - dists[i, j] = dists[i + len_2 * j]
    dists: list[int] = [0 for _ in range(0, len_1 * len_2)]

    # list_1 becomes empty by deleting everything
    for i in range(1, len_1):
        dists[i] = dists[i - 1] + list_1[i - 1].count
    
    # empty becomes list_2 by adding everything
    for j in range(1, len_2):
        dists[len_2 * j] = dists[len_2 * (j - 1)] + list_2[j - 1].count

    for j in range(0, len_2 - 1):
        for i in range(0, len_1 - 1):
            # substitution cost
            cost: int = list_1[i].count + list_2[j].count
            if list_1[i].name == list_2[j].name:
                cost = abs(list_1[i].count - list_2[j].count)

            # add distance to matrix, using previous entries
            dists[(i + 1) + len_2 * (j + 1)] = min(
                # delete from list 1
                dists[i + len_2 * (j + 1)] + list_1[i].count,
                # add from list 2
                dists[(i + 1) + len_2 * j] + list_2[j].count,
                # substitute
                dists[i + len_2 * j] + cost,
            )

    # final entry in matrix is the minimum distance
    return dists[(len_1 - 1) + len_2 * (len_2 - 1)]


### Tests ###

class __TestArmyClassifier(unittest.TestCase):

    def test_distance(self) -> None:
        faction: Faction = Faction("Ogor Mawtribes")

        army_list_1: FlatArmyList = FlatArmyList(
            faction = faction,
            warscrolls = [
                Warscroll("Frostlord on Stonehorn", 1),
                Warscroll("Huskard on Stonehorn", 1),
                Warscroll("Kragnos, The End of Empires", 1),
                Warscroll("Mournfang Pack", 3),
            ],
            enhancements = [
                Enhancement("Metalcruncher", 1),
                Enhancement("Nice Drop of the Red Stuff!", 1),
                Enhancement("Splatter-cleaver", 1),
            ],
        )

        army_list_2: FlatArmyList = FlatArmyList(
            faction = faction,
            warscrolls = [
                Warscroll("Frostlord on Stonehorn", 1),
                Warscroll("Kragnos, The End of Empires", 1),
                Warscroll("Mournfang Pack", 1),
                Warscroll("Stonehorn Beastriders", 2),
            ],
            enhancements = [
                Enhancement("Black Clatterhorn", 1),
                Enhancement("Nice Drop of the Red Stuff!", 1),
                Enhancement("Splatter-cleaver", 1),
            ],
        )

        # Warscrolls: delete 2 Mournfang Packs and 1 Huskard on Stonehorn, and 
        # add 2 Stonehorn Beastriders
        # Enhancements: substitute 1 Metalcruncher for 1 Black Clatterhorn
        expected: int = 5 + 2
        result: int = _distance(army_list_1, army_list_2)

        self.assertEqual(result, expected)

        # weighting warscrolls as 3 and enhancements as 2
        war_weight: int = 3
        enh_weight: int = 2
        expected: int = (5 * war_weight) + (2 * enh_weight)
        result: int = _distance(
            army_list_1 = army_list_1, 
            army_list_2 = army_list_2, 
            war_weight = war_weight, 
            enh_weight = enh_weight,
        )

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