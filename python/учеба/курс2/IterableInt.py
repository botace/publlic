# class IterableInt(int)

class IterableInt(int):
    def __len__(self):
        res = 0
        for _ in self: res += 1
        return res

    def __contains__(self, value):
        if not (0 <= value <= 9):
            raise ValueError('value должно быть цифрой 0...9')
        for d in self:
            if d == value:
                return True
        return False

    def slice_to_list(self, slice_obj):
        if not isinstance(slice_obj, slice):
            raise TypeError('Допустим только тип slice', type(slice_obj))
        raise NotImplementedError

    def __getitem__(self, idx):
        if isinstance( idx, slice):
            return self.slice_to_list( idx)

        if not isinstance(idx, int):
            raise TypeError('Индекс должен быть целым числом')

        if idx < 0:
            idx_positive = len(self) + idx
            if idx_positive < 0:
                raise IndexError('Вышли за диапазон')
            return self[idx_positive] # вызываем эту же ф-ию с положительным индексом

        for digit, index in self.__gen_private():
            if idx == index:
                return digit
        raise IndexError('Вышли за диапазон')

    def __gen_private(self):
        index = 0
        value = int(self)
        while value != 0:
            digit = value % 10
            value //= 10
            yield digit, index
            index += 1

    def __gen_public(self):
        value = int(self)
        while value != 0:
            digit = value % 10
            value //= 10
            yield digit

    def __iter__(self):
        return self.__gen_public();


if __name__ == '__main__':
    print( 'self test class IterableInt...')
    a = IterableInt(4678543)
    print( '>>>a = IterableInt(4678543)')
    print( '>>>print(a)')
    print(a)

    print( '>>>print( a + 10)')
    print( a + 10)

    print( '>>>print( a[0])')
    print( a[0])

    print( '>>>print( a[-1])')
    print( a[-1])

    print( '>>>print( a[2])')
    print( a[2])

    print( '>>>print( 9 in a)')
    print( 9 in a)

    print( '>>>print( 7 in a)')
    print( 7 in a)

    print( '>>>print( len(a))')
    print( len(a))

    print( '>>>print( [ai for ai in a])')
    print( [ai for ai in a])
