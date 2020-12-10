import random

class Weightable:
    """
    у этого класса нет атрибутов weights и value, к которому он обращается, но он есть у Rank и Suit
    """
    
    def __gt__(self, other):
        if not isinstance(other, Weightable):
            return NotImplemented
        return self.weight > other.weight

    def __lt__(self, other):
        if not isinstance(other, Weightable):
            return NotImplemented
        return self.weight < other.weight

    def __eq__(self, other):
        if not isinstance(other, Weightable):
            return NotImplemented
        return self.weight == other.weight

    def __ne__(self, other):
        if not isinstance(other, Weightable):
            return NotImplemented
        return self.weight != other.weight

    def __ge__(self, other):
        if not isinstance(other, Weightable):
            return NotImplemented
        return self.weight >= other.weight

    def __le__(self, other):
        if not isinstance(other, Weightable):
            return NotImplemented
        return self.weight <= other.weight

    @property
    def weight(self): # это метод, но снаружи выглядит как просто атрибут
        return self.weights[self.value]
    
    @weight.setter
    def weight(self, new_weight): # c1.rank.weight = 107 <- теперь можно так
        # как бы ищем в словаре по значениям, а не ключам
        for k, v in self.weights.items():
            if v == new_weight:
                new_value = k
                break
        else:
            # сюда попали если не произошло break'а
            # значит, нет такого веса
            raise ValueError('Нет такого веса', new_weight)
        
        self.value = new_value

class Rank(Weightable):
    weights = { # любые числа, лишь бы возрастали
        2: 101,
        3: 102,
        4: 103,
        5: 104,
        6: 105,
        7: 106,
        8: 107,
        9: 108,
        10: 109,
        'J': 110,
        'Q': 111,
        'K': 112,
        'A': 113
    }
    
    def __init__(self, name):
        # name - 2,3,4,5,6,7,8,9,10, J, Q, K, A
        if name not in self.weights.keys():
            raise ValueError('Неправильное значение карты', name)
        self.value = name # сохраняем как есть

    def __str__(self):
        return str(self.value)

    @classmethod
    def get_valid_values(cls): # тоже статичный метолд, но с аналогом self
        return cls.weights.keys() # атрибут всего класса, а не конкретного объекта

class Suit(Weightable):
    weights = {
        'hearts': 202,
        'clubs': 203,
        'diamonds': 201,
        'spades': 204,
    }
    symbols = {
        'hearts': '\u2665',
        'clubs': '\u2663',
        'diamonds': '\u2666',
        'spades': '\u2660',
    }
    
    def __init__(self, name):
        if name not in self.weights.keys():
            raise ValueError('Неправильная масть карты', name)
        self.value = name # сохраняем как есть

    def __str__(self):
        return self.symbols[self.value]
    
    @classmethod
    def get_valid_values(cls): # тоже статичный метолд, но с аналогом self
        return cls.weights.keys() # атрибут всего класса, а не конкретного объекта
    
class Card:
    def __init__(self, rank, suit):
        """
        rank - строка или число, например 2, 4, 'A', 'K'
        suit - название масти на английском 'hearts', 'spades'
        """
        self.suit = Suit(suit)
        self.rank = Rank(rank)
    
    def __repr__(self):
        return str(self.rank) + str(self.suit)
    
    def __eq__(self, other):
        return (self.rank == other.rank) and (self.suit == other.suit)
    
    def __gt__(self, other): # >
        """
        правила такие:
        если масть у обеих карт одинакова, сравниваются их значения (число или J Q K A)
        если масти разные, то больше та, у которой старше масть
        ♠>♣>♥>♦
        """
        if self.suit == other.suit:
            return self.rank > other.rank # свели к сравнению объектов Rank
        else:
            return self.suit > other.suit
    
    def __ge__(self, other): # >=
        return self > other or self == other
    
    @staticmethod
    def random(): # Статичный метод, работает без экземпляра
        r = random.choice(list(Rank.get_valid_values()))
        s = random.choice(list(Suit.get_valid_values()))
        return Card(r, s)
    
    @staticmethod
    def from_tuple(t): # конвертирует кортеж в карту
        if not isinstance(t, tuple):
            raise TypeError
        try:
            iter(t)
            return [Card(*obj) for obj in t]
        except: pass
        return Card(*t) # Card(r, s)

    def __hash__(self):
        # собрали кортеж из двух чисел и посчитали
        return hash((self.rank.weight, self.suit.weight))
        
