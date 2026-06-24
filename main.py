from enum import StrEnum, auto
from fractions import Fraction

class Action(StrEnum):
    CHECK = 'x'
    BET   = 'b'
    FOLD  = 'f'
    CALL  = 'c'

next_actions: dict[str, list[str] | None] = {
    '':    ['b', 'x'],
    'b':   ['c', 'f'],
    'x':   ['b', 'x'],
    'bc':  None,
    'bf':  None,
    'xx':  None,
    'xb':  ['c', 'f'],
    'xbc': None,
    'xbf': None
}

class Card(StrEnum):
    JACK  = auto()
    QUEEN = auto()
    KING  = auto()

    def __gt__(self, other):
        if isinstance(other, Card):
            return list(Card).index(self) > list(Card).index(other)
        return NotImplemented

otherCards: dict[Card,list[Card]] = {
    Card.KING:  [Card.QUEEN, Card.JACK],
    Card.QUEEN: [Card.KING, Card.JACK],
    Card.JACK:  [Card.KING, Card.QUEEN]
}

def compare_cards(c1: Card, c2: Card) -> bool:
    return c1 > c2

def calc_terminals(actions: str, c1: Card, c2: Card) -> int:
    match actions:
        case 'bc' | 'xbc':  
            return 2 if compare_cards(c1, c2) else -2
        case 'bf':  
            return 1
        case 'xbf': 
            return -1
        case 'xx':
            return 1 if compare_cards(c1, c2) else -1
        case _:
            return None

class Node:
    def __init__(self, c1: Card, c2: Card, prevActions: list[str]):
        self.c1 = c1
        self.c2 = c2
        self.prevActions = prevActions
        self.nextActions: list[str] | None = next_actions[''.join(self.prevActions)]
        self.terminal_utility: int = None
    
    def __str__(self):
        return f'\nNode: {self.c1=} {self.c2=} {self.prevActions} {self.nextActions} {self.terminal_utility}'
    
    def __repr__(self):
        return self.__str__()

class InfoSet:
    def __init__(self, 
                 level: int, 
                 c1: Card | None, 
                 c2: Card | None, 
                 actions: str):
        self.level   = level
        self.c1      = c1
        self.c2      = c2
        self.actions = actions
        self.nodes   = set()
    
    def __str__(self):
        return f'InfoSet {self.level} {self.c2 if not self.c1 else self.c1} {self.actions} {self.nodes}'
    
    def __hash__(self):
        c = self.c1 if self.c1 is not None else self.c2
        return hash(str(self.level)+c+self.actions)
    
    def __eq__(self, other):
        return (self.c1==other.c1) and \
               (self.c2==other.c2) and \
               (self.actions==other.actions) and \
               (self.level==other.level)

def create_next_infosets(level, prevIS=None) -> set[InfoSet]:
    if level == 1:
        nfosets = set(InfoSet(level=level, c1=c, c2=None, actions='') for c in Card)
        for i in nfosets:
            for c in otherCards[i.c1]:
                i.nodes.add(Node(i.c1, c, i.actions))
    else:
        nfosets = set()
        for i1 in prevIS:
            for node in i1.nodes:
                if node.nextActions:
                    for a in node.nextActions:
                        if level%2==0:
                            nfosets.add(InfoSet(level=level, c1=None, c2=node.c2, actions=node.prevActions+a))
                        else:
                            nfosets.add(InfoSet(level=level, c1=node.c2, c2=None, actions=node.prevActions+a))
        for i2 in nfosets:
            if level%2==0:
                for c in otherCards[i2.c2]:
                    i2.nodes.add(Node(c, i2.c2, i2.actions))
            else:
                for c in otherCards[i2.c1]:
                    i2.nodes.add(Node(i2.c1, c, i2.actions))
    for i in nfosets:
        for n in i.nodes:
            tu = calc_terminals(n.prevActions, n.c1, n.c2)
            if tu:
                n.terminal_utility = tu
    for i in nfosets:
        print(i)
    return nfosets

def initialize_strategies(nfosets: set[InfoSet]) -> dict[[Node, str], Fraction]:
    return {(n, a): Fraction(1,2) for i in nfosets for n in i.nodes if n.nextActions for a in n.nextActions}

def main():
    is1 = create_next_infosets(level=1)
    is2 = create_next_infosets(level=2, prevIS=is1)
    is3 = create_next_infosets(level=3, prevIS=is2)
    is4 = create_next_infosets(level=4, prevIS=is3)
    strategies = initialize_strategies(is1|is2|is3|is4)


if __name__ == "__main__":
    main()