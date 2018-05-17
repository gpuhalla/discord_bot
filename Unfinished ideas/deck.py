from random import shuffle
from card import card

class deck:
    FULLDECK = []

    def __init__(self):
        self.shuffle()

    def shuffle(self):
        # and then shuffle
        self.cards = deck.getFullDeck()
        shuffle(self.cards)

    def draw(self, n=1):
        cards = []
        for i in range(n):
            cards.append(self.cards.pop(0))
        return cards
	
	def mill(self, n=1)
        for i in range(n):
            self.cards.pop(0)

    def __str__(self):
        return card.print_pretty_cards(self.cards)

    @staticmethod
    def GetFullDeck():
        if deck.FULLDECK:
            return list(deck.FULLDECK)

        # create the standard 52 card deck
        for rank in card.RANKS:
            for suit in card.SUITS:
                deck.FULLDECK.append(card(rank, suit))

        return list(deck.FULLDECK)