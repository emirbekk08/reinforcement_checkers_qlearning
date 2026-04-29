"""
checkers_engine.py — общая логика шашек для train.py и play.py

Правила:
- Простая шашка ходит вперёд, бьёт во все 4 стороны (назад тоже).
- Дамка ходит по диагонали на любое расстояние, бьёт через врага
  и встаёт на любую клетку за ним.
- Взятие ОБЯЗАТЕЛЬНО. Если можно бить — надо бить.
- Цепочка взятий: после взятия, если можно бить ещё — обязан продолжить.
  Вся цепочка считается одним "ходом" (список клеток).
"""

import numpy as np

SIZE = 8


# ──────────────────────────────────────────────────────────────
#  ОДИНОЧНЫЕ ВЗЯТИЯ (один прыжок)
# ──────────────────────────────────────────────────────────────
def _single_jumps(board, r, c, exclude=None):
    """
    Возвращает список одиночных взятий для фигуры на (r,c).
    exclude — множество клеток уже съеденных врагов (для цепочки).
    Формат: (r, c, land_r, land_c, kill_r, kill_c)
    """
    if exclude is None:
        exclude = set()
    piece  = board[r][c]
    if piece == 0:
        return []
    player = 1 if piece > 0 else -1
    jumps  = []

    if abs(piece) == 2:                          # ДАМКА
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc    = r+dr, c+dc
            found_pos = None
            while 0 <= nr < SIZE and 0 <= nc < SIZE:
                cell = board[nr][nc]
                if found_pos is None:
                    if (nr, nc) in exclude:
                        pass                     # уже съеденная — пропускаем
                    elif np.sign(cell) == -player:
                        found_pos = (nr, nc)     # нашли врага
                    elif cell != 0:
                        break                    # своя — стоп
                else:
                    if cell == 0:
                        jumps.append((r, c, nr, nc, found_pos[0], found_pos[1]))
                    else:
                        break                    # кто-то стоит — стоп
                nr += dr; nc += dc

    else:                                        # ПРОСТАЯ ШАШКА
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r+dr, c+dc
            jr, jc = r+2*dr, c+2*dc
            if 0 <= jr < SIZE and 0 <= jc < SIZE:
                mid = board[nr][nc]
                if (nr,nc) not in exclude and np.sign(mid)==-player and board[jr][jc]==0:
                    jumps.append((r, c, jr, jc, nr, nc))
    return jumps


# ──────────────────────────────────────────────────────────────
#  ЦЕПОЧКИ ВЗЯТИЙ (рекурсия)
# ──────────────────────────────────────────────────────────────
def _all_chains(board, r, c, killed):
    """
    Рекурсивно строит все цепочки взятий начиная с (r,c).
    killed — множество уже съеденных клеток в текущей цепочке.
    Возвращает список цепочек вида [(land_r, land_c, kill_r, kill_c), ...].
    """
    nexts = _single_jumps(board, r, c, exclude=killed)
    if not nexts:
        return [[]]                              # конец цепочки

    all_seqs = []
    for j in nexts:
        _, _, lr, lc, kr, kc = j
        new_killed = killed | {(kr, kc)}

        # Временно применяем прыжок для рекурсии
        tmp = board.copy()
        tmp[lr][lc] = tmp[r][c]
        tmp[r][c]   = 0
        # Не убираем врага сразу — он «заморожен» до конца цепочки
        # (стандартное русское правило)

        for tail in _all_chains(tmp, lr, lc, new_killed):
            all_seqs.append([(lr, lc, kr, kc)] + tail)

    return all_seqs


def get_jump_moves(board, player):
    """
    Все цепочки взятий для игрока.
    Возвращает список ходов, каждый ход = tuple:
      (start_r, start_c, [(land_r, land_c, kill_r, kill_c), ...])
    """
    results = []
    for r in range(SIZE):
        for c in range(SIZE):
            if np.sign(board[r][c]) != player:
                continue
            chains = _all_chains(board, r, c, set())
            for chain in chains:
                if chain:                        # непустая цепочка
                    results.append((r, c, chain))
    return results


# ──────────────────────────────────────────────────────────────
#  ОБЫЧНЫЕ ХОДЫ (без взятия)
# ──────────────────────────────────────────────────────────────
def get_simple_moves(board, player):
    moves = []
    for r in range(SIZE):
        for c in range(SIZE):
            piece = board[r][c]
            if np.sign(piece) != player:
                continue
            if abs(piece) == 2:                  # дамка
                for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                    nr, nc = r+dr, c+dc
                    while 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == 0:
                        moves.append((r, c, [(nr, nc)]))
                        nr += dr; nc += dc
            else:                                # простая
                dirs = [(-1,-1),(-1,1)] if piece == 1 else [(1,-1),(1,1)]
                for dr, dc in dirs:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < SIZE and 0 <= nc < SIZE and board[nr][nc] == 0:
                        moves.append((r, c, [(nr, nc)]))
    return moves


# ──────────────────────────────────────────────────────────────
#  ПОЛУЧИТЬ ВСЕ ХОДЫ
# ──────────────────────────────────────────────────────────────
def get_moves(board, player):
    """
    Если есть взятия — возвращает только их (обязательное взятие).
    Иначе — простые ходы.
    Формат хода: (start_r, start_c, [(step_r, step_c[, kill_r, kill_c]), ...])
      Для взятий каждый шаг = (land_r, land_c, kill_r, kill_c)
      Для простых ходов    = (land_r, land_c)
    """
    jumps = get_jump_moves(board, player)
    if jumps:
        return jumps
    return get_simple_moves(board, player)


# ──────────────────────────────────────────────────────────────
#  ПРИМЕНИТЬ ХОД
# ──────────────────────────────────────────────────────────────
def do_move(board, move):
    """
    Применяет ход (включая цепочку взятий).
    Возвращает новую доску и количество съеденных фигур.
    """
    b = board.copy()
    r, c, steps = move
    taken = 0

    for step in steps:
        nr, nc = step[0], step[1]
        b[nr][nc] = b[r][c]
        b[r][c]   = 0
        if len(step) == 4:                       # это взятие
            b[step[2]][step[3]] = 0
            taken += 1
        r, c = nr, nc

    # Превращение в дамку
    if b[r][c] == 1  and r == 0:      b[r][c] = 2
    if b[r][c] == -1 and r == SIZE-1: b[r][c] = -2

    return b, taken


# ──────────────────────────────────────────────────────────────
#  СОСТОЯНИЕ И ПОБЕДИТЕЛЬ
# ──────────────────────────────────────────────────────────────
def get_state(board):
    return board.tobytes()


def check_winner(board, steps):
    if np.sum(board < 0) == 0:     return 1    #  игрок (красные)
    if np.sum(board > 0) == 0:     return -1   #  AI    (серые)
    if not get_moves(board,  1):   return -1
    if not get_moves(board, -1):   return 1
    if steps >= 200:               return 0    #  ничья
    return None


# ──────────────────────────────────────────────────────────────
#  НАЧАЛЬНАЯ ДОСКА
# ──────────────────────────────────────────────────────────────
def make_board():
    b = np.zeros((SIZE, SIZE), dtype=int)
    for r in range(3):
        for c in range(SIZE):
            if (r+c)%2 == 1: b[r][c] = -1   # серые (AI, сверху)
    for r in range(5, SIZE):
        for c in range(SIZE):
            if (r+c)%2 == 1: b[r][c] = 1    # красные (игрок, снизу)
    return b