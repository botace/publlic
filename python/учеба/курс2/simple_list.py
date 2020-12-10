# simple list realisation

class SLL:
    class __Item:
        def __init__(self, value=None, next=None):
            self.value = value
            self.next = next

    def __init__(self, some=None):
        self.head = None
        if some is None:
            return
        if not hasattr(some, '__iter__'):
            raise TypeError('Только итеративные объекты')
        for ai in some:
            self.append(ai)

    def gen_public(self):
        pos = self.head
        while pos is not None:
            yield pos.value
            pos = pos.next

    def __gen_private(self):
        index = 0
        pos = self.head
        while pos is not None:
            yield pos, index
            index += 1
            pos = pos.next

    def __iter__(self):
        return self.gen_public()

    def __repr__(self):
        res = 'SLL(['
        for obj, idx in self.__gen_private():
            if idx != 0: res += ', '
            res += (obj.value).__repr__()
        res += '])'
        return res

    def __len__(self):
        res = 0
        for _ in self.__gen_private():
            res += 1
        return res

    def __getitem__(self, idx):
        if not isinstance(idx, int):
            raise TypeError('Индекс должен быть целым числом')

        if idx < 0:
            idx_positive = len(self) + idx
            if idx_positive < 0:
                raise IndexError('Вышли за диапазон')
            return self[idx_positive] # вызываем эту же ф-ию с положительным индексом

        for item, index in self.__gen_private():
            if idx == index:
                return item.value
        raise IndexError('Вышли за диапазон')

    def append(self, value):
        for item, _ in self.__gen_private():
            if item.next is None:
                item.next = SLL.__Item(value)
                break
        else:
            self.head = SLL.__Item(value)

    def remove(self, value):
        prev = self.head
        for item, idx in self.__gen_private():
            if item.value == value:
                prev.next = item.next
                if idx == 0:
                    self.head = prev.next
                return True
            prev = item
        return False


if __name__ == '__main__':
    a = SLL()
    a.append(5)
    print(a)
    a.remove(5)
    print(a)
    a.append(5)
    a.append(10)
    a.append('hello')
    a.append(-123)
    print(a)
    print(len(a))

    b = SLL(a)
    b.append(999)
    print(b)
    b.remove('hello')
    print(b)

    print(a[0])
    print(a[3])

    print(a[-3])
    print(a[-1])

    print(-123 in a)
    print('hello' in a)
    print(100 in a)

    d = [ai for ai in a]
    print(d)