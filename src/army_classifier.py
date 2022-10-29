from collections import Counter
from dataclasses import dataclass
from typing import TypeVar
from army_flattener import *
import unittest

# TODO: add a discursive document explaining hyperparameter selection

### Data classes ###

@dataclass(frozen = True, order = True)
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

def classify(
    army_list: FlatArmyList,
    bank: KnowledgeBank,
    k: int = 1,
    dist_weighted: bool = False,
    war_weight: int = 2,
    enh_weight: int = 1,
) -> Archetype | None:
    """
    Classify an army list into a particular archetype using a knowledge bank.

    If no archetypes of the same faction as the passed army list exist in the
    knowledge bank 'None' is returned, otherwise the majority voted archetype.

    The labelled army list is not added to the knowledge bank.

    k-nearest neighbours is used for classification, with proximity
    defined using the Levenshtein distance between two army lists.

    Hyperparameters:
    k             - the number of neighbours that vote on the archetype;
    dist_weighted - whether to weight the votes by their inverse distance;
    war_weight    - weight of each warscroll distance;
    enh_weight    - weight of each enhancement distance.
    """

    faction: Faction = army_list.faction
    dists: list[tuple[int, Archetype]] = []
    for arc, a_ls in bank.data.items():
        # look only at archetypes of the same faction
        if arc.faction == faction:
            # get distances to each army list in the archetype
            new_dists: list[tuple[int, Archetype]] = [
                (_distance(army_list, a_l, war_weight, enh_weight), arc) 
                for a_l 
                in a_ls
            ]
            dists.extend(new_dists)
    
    if len(dists) == 0:
        # no archetypes are found in knowledge bank
        return None
    else:
        # sort the distances in ascending order
        dists.sort()

        # take the closest k archetypes and find the most common
        arc: Archetype
        if dist_weighted:
            # weight votes by distance
            arc = _weighted_vote(dists[0:k])
        else:
            # treat each vote equally
            counts: Counter[Archetype] = Counter([arc for _, arc in dists[0:k]])
            arc = counts.most_common(1)[0][0]
        return arc

def add_to_bank(
    archetype: Archetype,
    army_list: FlatArmyList,
    bank: KnowledgeBank,
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


### Private ###

def _distance(
    army_list_1: FlatArmyList,
    army_list_2: FlatArmyList,
    war_weight: int = 1,
    enh_weight: int = 1,
) -> int:
    """
    Calculate the Levenshtein distance between two army lists.

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
    """
    Levenshtein distance between two lists of army list items.

    In most cases the two lists should be sorted for best results.

    A mostly standard Levenshtein distance implementation, notable choices are
    substitution being costed equivalent to addition plus deletion, and item 
    counts being used for costs - e.g. adding 1 item with count 3 costs 3.
    """

    if len(list_1) == 0:
        return sum([item.count for item in list_2])
    elif len(list_2) == 0:
        return sum([item.count for item in list_1])

    # extend lengths by 1 to include row and column 0 in distance matrix
    len_1: int = len(list_1) + 1
    len_2: int = len(list_2) + 1

    # initialise all distance matrix values to 0
    # use a list to represent matrix - dists[i, j] = dists[i + len_1 * j]
    dists: list[int] = [0 for _ in range(0, len_1 * len_2)]

    # row 0 - list_1 becomes empty by deleting everything
    for i in range(1, len_1):
        dists[i] = dists[i - 1] + list_1[i - 1].count

    # column 0 - empty becomes list_2 by adding everything
    for j in range(1, len_2):
        dists[len_1 * j] = dists[len_1 * (j - 1)] + list_2[j - 1].count
    
    for j in range(1, len_2):
        for i in range(1, len_1):
            # substitution cost
            cost: int = list_1[i - 1].count + list_2[j - 1].count
            if list_1[i - 1].name == list_2[j - 1].name:
                cost = abs(list_1[i - 1].count - list_2[j - 1].count)

            # add minimum distance to matrix
            dists[i + len_1 * j] = min(
                # delete from list 1
                dists[(i - 1) + len_1 * j] + list_1[i - 1].count,
                # add from list 2
                dists[i + len_1 * (j - 1)] + list_2[j - 1].count,
                # substitute
                dists[(i - 1) + len_1 * (j - 1)] + cost,
            )
    
    # final entry in matrix is the minimum distance
    return dists[(len_1 - 1) + len_1 * (len_2 - 1)]

def _weighted_vote(dists: list[tuple[int, Archetype]]) -> Archetype:
    # weight by inverse distance
    w_dists: list[tuple[float, Archetype]] = [
        ((1.0 / d), arc)
        for d, arc 
        in dists
    ]

    # count votes for each archetype
    votes: dict[Archetype, float] = {}
    for w_d, arc in w_dists:
        v: float = votes.setdefault(arc, 0.0)
        votes[arc] = v + w_d
    
    # return the archetype with the most votes
    return max(votes, key = votes.get) # type: ignore


### Tests ###

class __TestArmyClassifier(unittest.TestCase):

    def test_classify(self) -> None:
        bank: KnowledgeBank = KnowledgeBank({})
        faction: Faction = Faction("Ogor Mawtribes")

        # build knowledge bank with two prototype army lists
        archetype_1: Archetype = Archetype(
            faction = faction,
            name = "Kragnos Beastclaw Raiders"
        )
        prototype_1: FlatArmyList = FlatArmyList(
            faction = faction,
            warscrolls = [
                Warscroll("Kragnos, The End of Empires", 1),
                Warscroll("Frostlord on Stonehorn", 1),
            ],
            enhancements = [],
        )
        add_to_bank(archetype_1, prototype_1, bank)

        archetype_2: Archetype = Archetype(
            faction = faction,
            name = "Incarnate Beastclaw Raiders"
        )
        prototype_2: FlatArmyList = FlatArmyList(
            faction = faction,
            warscrolls = [
                Warscroll('Frostlord on Stonehorn', 1),
                Warscroll('Krondspine Incarnate of Ghur', 1),
            ], 
            enhancements = [],
        )
        add_to_bank(archetype_2, prototype_2, bank)

        # Classify an army list of a different faction
        army_list_0: FlatArmyList = FlatArmyList(
            faction = Faction("Ironjawz"),
            warscrolls = [],
            enhancements = [],
        )
        expected: Archetype | None = None
        result: Archetype | None = classify(army_list_0, bank)

        self.assertEqual(result, expected)

        # Classify an army list of the first archetype
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

        expected: Archetype | None = archetype_1
        result: Archetype | None = classify(army_list_1, bank)

        self.assertEqual(result, expected)

        # Classify an army list of the second archetype
        army_list_2: FlatArmyList = FlatArmyList(
            faction = faction,
            warscrolls = [
                Warscroll('Frost Sabres', 1),
                Warscroll('Frostlord on Stonehorn', 1),
                Warscroll('Krondspine Incarnate of Ghur', 1),
                Warscroll('Mournfang Pack', 2),
                Warscroll('Slaughtermaster', 1),
                Warscroll('Stonehorn Beastriders', 2),
            ], 
            enhancements = [
                Enhancement('Metalcruncher', 1),
                Enhancement('Molten Entrails', 1),
                Enhancement('Nice Drop of the Red Stuff!', 1),
                Enhancement('Ribcracker', 1),
                Enhancement('Splatter-cleaver', 1),
            ],
        )

        expected: Archetype | None = archetype_2
        result: Archetype | None = classify(army_list_2, bank)

        self.assertEqual(result, expected)

        # no classified army lists should be in the bank
        self.assertEqual(len(bank.data.keys()), 2)
        for a_ls in bank.data.values():
            self.assertEqual(len(a_ls), 1)

    def test_add_to_bank(self) -> None:
        bank: KnowledgeBank = KnowledgeBank({})
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
        add_to_bank(
            archetype = archetype_1,
            army_list = army_list_1,
            bank = bank,
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
                Warscroll('Krondspine Incarnate of Ghur', 1),
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

    def test_lev_distance(self) -> None:
        # empty lists give 0 distance
        l_1: list[Warscroll] = []
        l_2: list[Warscroll] = []

        self.assertEqual(_lev_distance(l_1, l_2), 0)

        # one empty list gives the total count of the other
        l_1: list[Warscroll] = [
            Warscroll("Frostlord on Stonehorn", 1),
            Warscroll("Huskard on Stonehorn", 1),
            Warscroll("Kragnos, The End of Empires", 1),
            Warscroll("Mournfang Pack", 3),
        ]
        l_2: list[Warscroll] = []

        self.assertEqual(_lev_distance(l_1, l_2), 6)
        self.assertEqual(_lev_distance(l_2, l_1), 6)

        # two non-empty lists give the correct distance
        l_1: list[Warscroll] = [
            Warscroll("Frostlord on Stonehorn", 1),
            Warscroll("Huskard on Stonehorn", 1),
            Warscroll("Kragnos, The End of Empires", 1),
            Warscroll("Mournfang Pack", 3),
        ]
        l_2: list[Warscroll] = [
            Warscroll("Frostlord on Stonehorn", 1),
            Warscroll("Kragnos, The End of Empires", 1),
            Warscroll("Stonehorn Beastriders", 2),
        ]

        # TODO: fix issues with non square matrices
        self.assertEqual(_lev_distance(l_1, l_2), 6)
        self.assertEqual(_lev_distance(l_2, l_1), 6)
    
    def test_weighted_vote(self) -> None:
        archetype_1: Archetype = Archetype(Faction("A"), "A")
        archetype_2: Archetype = Archetype(Faction("B"), "B")
        dists: list[tuple[int, Archetype]]

        # closest vote wins
        # 1/2 > 1/4 + 1/5
        dists = [
            (2, archetype_1),
            (4, archetype_2),
            (5, archetype_2),
        ]
        self.assertEqual(_weighted_vote(dists), archetype_1)

        # votes are tied, choose closest
        # 1/2 = 1/4 + 1/4
        dists = [
            (2, archetype_1),
            (4, archetype_2),
            (4, archetype_2),
        ]
        self.assertEqual(_weighted_vote(dists), archetype_1)

        # further votes win
        # 1/2 < 1/3 + 1/4
        dists = [
            (2, archetype_1),
            (3, archetype_2),
            (5, archetype_2),
        ]
        self.assertEqual(_weighted_vote(dists), archetype_2)


if __name__ == '__main__':
    unittest.main()