""" Набор общих функций для применения в проектах
"""

# Функция проверяет строку на допустимость конвертации её в float
def str2float(st: str, default=float()):
    if type(st) == str and (st.replace(',', '').isdigit() or st.replace('.', '').isdigit()):
        return float(st.replace(',', '.'))
    return default

# Функция проверяет строку на допустимость конвертации её в int
def str2int(st: str, default=int()):
    if type(st) == str and len(st) and st.isdigit():
        return int(st)
    return default

# Функция проверяет итирируемый обьект, что все его элементы одного типа
def istype_in(obj, need_type=None):
    if need_type is None:
        need_type = type(obj[0])
    for item in obj:
        if type(item) != need_type:
            return False
    return True

# Функция печатает строку с прогресс-баром
def pbprint(prefix: str, percent: int, comment: str):
    char_progress = '\u2588'
    percent = percent if 0 <= percent < 100 else 100
    prefix = prefix[:20]
    comment = comment[:75]
    i1 = int(percent * 2.2 / 22 * 2.2)
    progress = char_progress * i1 + ' ' * (22 - i1)
    print("%s [%s %3d%%] %-75s" % (prefix, progress, percent, comment), end='\n' if percent >= 100 else '\r')


if __name__ == '__main__':

    import time

    for i in range(0, 101, 2):
        pbprint('test', i, f'{i}')
        time.sleep(1)
