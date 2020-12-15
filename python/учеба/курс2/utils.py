""" Набор общих функций для применения в проектах
"""


# Функция печатает строку с прогресс-баром
def pbprint(prefix: str, percent: int, comment: str):
    char_progress = '\u2588'
    percent = percent if 0 <= percent < 100 else 100
    prefix = prefix[:20]
    comment = comment[:80]
    i1 = int(percent * 2.2 / 22 * 2.2)
    progress = char_progress * i1 + ' ' * (22 - i1)
    print("%s [%s %3d%%] %-75s" % (prefix, progress, percent, comment), end='\n' if percent >= 100 else '\r')


if __name__ == '__main__':

    import time

    for i in range(0, 101, 2):
        pbprint('test', i, f'{i}')
        time.sleep(1)
