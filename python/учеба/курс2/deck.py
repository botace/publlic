import random
import itertools
import cards

class Deck:
    def __init__(self):
        self.new_deck()

    def new_deck(self):
        self.deck=[
            cards.Card(r,s) for r,s in itertools.product(
                    cards.Rank.get_valid_values(),
                    cards.Suit.get_valid_values())
        ]
        self.deck.sort()

    def __repr__(self):
        return self.deck.__repr__()

    def __str__(self):
        return self.deck.__str__()

    def __len__(self):
        return self.deck.__len__()

    def __getitem__(self, idx):
        return self.deck.__getitem__(idx)

    def __iter__(self):
        return self.deck.__iter__()

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self, n):
        if n < 1: return set()
        return {self.deck.pop() for _ in range(min(n,len(self.deck)))}

if __name__ == '__main__':
    # # 4. Сделать класс "колода"
    # Создаём колоду
    d = Deck() # 52 карты, отсортированные

    # Перемешиваем колоду
    d.shuffle()

    # Достали 5 карт из колоды
    hand = d.draw(5)

    print(hand)
    print(d)