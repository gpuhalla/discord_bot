class card:
	RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] 
	SUITS = ["SPADES", "HEARTS", "CLUBS", "DIAMONDS"] 
	def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.card = self.rank, self.suit