"""
play.py — игра Человек vs AI.
AI использует q_merged.pkl (объединение Q1+Q2 из merge.py).
Логика шашек из checkers_engine.py (та же что в train.py).
"""

import pygame
import pickle
import numpy as np
import os
import sys
import random

from checkers_engine import (
    SIZE, make_board, get_moves, do_move, check_winner, get_state
)

# ──────────────────────────────────────────
#  НАСТРОЙКИ ОКНА
# ──────────────────────────────────────────
CELL   = 75
WIDTH  = SIZE * CELL
HEIGHT = SIZE * CELL + 110

C_BG         = (18, 18, 24)
C_LIGHT      = (240, 217, 181)
C_DARK       = (181, 136,  99)
C_RED        = (200,  35,  35)
C_RED_SHINE  = (255, 110, 110)
C_GRAY       = ( 60,  60,  70)
C_GRAY_SHINE = (120, 120, 140)
C_GOLD       = (255, 200,   0)
C_HINT       = (255, 220,   0)
C_PANEL      = ( 22,  22,  30)
C_DIM        = (160, 160, 175)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Шашки — Человек vs AI")
clock = pygame.time.Clock()

font_lg = pygame.font.SysFont("Georgia",     42, bold=True)
font_md = pygame.font.SysFont("Georgia",     22, bold=True)
font_sm = pygame.font.SysFont("Courier New", 15)

# ──────────────────────────────────────────
#  ЗАГРУЗКА МОДЕЛИ
# ──────────────────────────────────────────
Q: dict = {}
model_size = 0
for path in ["model/q_merged.pkl", "model/q_ai.pkl"]:
    if os.path.exists(path):
        with open(path, "rb") as f:
            Q = pickle.load(f)
        model_size = len(Q)
        print(f"Загружено: {path}  ({model_size:,} позиций)")
        break
else:
    print("Модель не найдена — AI играет случайно")


def ai_choose(board):
    moves = get_moves(board, -1)
    if not moves:
        return None
    if not Q:
        return random.choice(moves)
    state = get_state(board)
    return max(moves, key=lambda m: Q.get((state, str(m)), 0.0))


# ──────────────────────────────────────────
#  РИСОВАНИЕ
# ──────────────────────────────────────────
def draw_piece(r, c, piece):
    cx  = c * CELL + CELL // 2
    cy  = r * CELL + CELL // 2
    rad = CELL // 2 - 7
    if piece > 0:
        col, shine, rim = C_RED, C_RED_SHINE, (100, 10, 10)
    else:
        col, shine, rim = C_GRAY, C_GRAY_SHINE, (15, 15, 20)

    pygame.draw.circle(screen, (0,0,0),  (cx+3, cy+4), rad)
    pygame.draw.circle(screen, rim,      (cx,   cy),   rad+2)
    pygame.draw.circle(screen, col,      (cx,   cy),   rad)
    pygame.draw.circle(screen, shine,    (cx - rad//4, cy - rad//4), rad//3)
    if abs(piece) == 2:
        pygame.draw.circle(screen, C_GOLD, (cx, cy), rad - 8, 3)


def draw_all(board, selected, hints, winner, steps, ai_thinking, turn,
             chain_pos, chain_hints):
    screen.fill(C_BG)

    # Доска
    for r in range(SIZE):
        for c in range(SIZE):
            col = C_LIGHT if (r+c)%2==0 else C_DARK
            pygame.draw.rect(screen, col, (c*CELL, r*CELL, CELL, CELL))

        # Подсветка выбранной
    if selected:
        r, c = selected
        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        s.fill((80, 230, 80, 90))
        screen.blit(s, (c*CELL, r*CELL))

    # Подсветка текущей позиции цепочки
    if chain_pos:
        r, c = chain_pos
        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        s.fill((80, 150, 255, 100))
        screen.blit(s, (c*CELL, r*CELL))

    # Подсказки (обычные или цепочка)
    active_hints = chain_hints if chain_pos else hints
    for step in active_hints:
        nr, nc = step[0], step[1]
        dx = nc * CELL + CELL // 2
        dy = nr * CELL + CELL // 2
        pygame.draw.circle(screen, C_HINT, (dx, dy), 11)
        pygame.draw.circle(screen, (0,0,0), (dx, dy), 11, 2)

    # Фигуры
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != 0:
                draw_piece(r, c, board[r][c])

    # Панель
    py = SIZE * CELL
    pygame.draw.rect(screen, C_PANEL, (0, py, WIDTH, 110))
    pygame.draw.line(screen, (50,50,70), (0, py), (WIDTH, py), 2)

    if winner:
        msgs = {1: ("ВЫ ПОБЕДИЛИ!", (80,220,80)),
                -1: ("AI ПОБЕДИЛ",  (220,80,80)),
                0:  ("НИЧЬЯ",        C_GOLD)}
        msg, col = msgs[winner]
        t = font_lg.render(msg, True, col)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, py + 8))
        h = font_sm.render("Нажми  R  — новая игра", True, C_DIM)
        screen.blit(h, (WIDTH//2 - h.get_width()//2, py + 72))
    else:
        if chain_pos:
            msg, col = "Продолжай бить!  ●  выбери клетку", (255, 180, 0)
        elif ai_thinking:
            msg, col = "AI думает...", (120, 180, 255)
        elif turn == 1:
            msg, col = "Ваш ход  ●  Красные", C_RED
        else:
            msg, col = "Ход AI  ●  Серые", C_GRAY_SHINE

        t = font_md.render(msg, True, col)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, py + 10))

        red_n  = int(np.sum(board > 0))
        gray_n = int(np.sum(board < 0))
        info = font_sm.render(
            f"🔴 ×{red_n}   ⚫ ×{gray_n}   Ходов: {steps}   AI: {model_size:,} поз.",
            True, C_DIM)
        screen.blit(info, (WIDTH//2 - info.get_width()//2, py + 50))
        tip = font_sm.render("R = рестарт  |  клик — выбрать шашку", True, (60,60,80))
        screen.blit(tip, (WIDTH//2 - tip.get_width()//2, py + 82))

    pygame.display.flip()


# ──────────────────────────────────────────
#  ПОЛУЧИТЬ СЛЕДУЮЩИЕ ВЗЯТИЯ ДЛЯ ЦЕПОЧКИ
# ──────────────────────────────────────────
def next_chain_steps(board, r, c, killed):
    """Возвращает список следующих одиночных взятий из (r,c), исключая killed."""
    from checkers_engine import _single_jumps
    return _single_jumps(board, r, c, exclude=killed)


# ──────────────────────────────────────────
#  ГЛАВНЫЙ ЦИКЛ
# ──────────────────────────────────────────
def reset():
    return dict(
        board       = make_board(),
        selected    = None,
        hints       = [],          # подсказки для выбора шашки
        winner      = None,
        turn        = 1,
        steps       = 0,
        ai_thinking = False,
        ai_delay    = 0,
        # Цепочка взятий игрока
        chain_pos   = None,        # (r,c) текущей позиции при цепочке
        chain_board = None,        # доска после частичных взятий
        chain_killed= None,        # уже съеденные в цепочке
        chain_hints = [],          # возможные следующие прыжки
    )


def main():
    st = reset()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                st = reset()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if st["winner"] or st["ai_thinking"]:
                    continue
                if st["turn"] != 1:
                    continue

                mx, my = event.pos
                c = mx // CELL
                r = my // CELL
                if not (0 <= r < SIZE and 0 <= c < SIZE):
                    continue

                # ── Режим цепочки взятий ────────────────
                if st["chain_pos"] is not None:
                    cr, cc = st["chain_pos"]
                    clicked = next(
                        (j for j in st["chain_hints"] if j[2]==r and j[3]==c),
                        None
                    )
                    if clicked:
                        _, _, lr, lc, kr, kc = clicked
                        # Применяем один прыжок
                        b = st["chain_board"].copy()
                        b[lr][lc] = b[cr][cc]
                        b[cr][cc] = 0
                        new_killed = st["chain_killed"] | {(kr, kc)}

                        # Дамка?
                        if b[lr][lc] == 1  and lr == 0:        b[lr][lc] = 2
                        if b[lr][lc] == -1 and lr == SIZE-1:   b[lr][lc] = -2

                        # Есть ли ещё взятия?
                        from checkers_engine import _single_jumps
                        nxt = _single_jumps(b, lr, lc, exclude=new_killed)

                        if nxt:
                            # Продолжаем цепочку
                            st["chain_board"]  = b
                            st["chain_pos"]    = (lr, lc)
                            st["chain_killed"] = new_killed
                            st["chain_hints"]  = nxt
                        else:
                            # Цепочка завершена — убираем всех съеденных
                            for kr2, kc2 in new_killed:
                                b[kr2][kc2] = 0
                            st["board"]      = b
                            st["steps"]     += 1
                            st["chain_pos"]  = None
                            st["chain_board"]= None
                            st["chain_killed"]= None
                            st["chain_hints"] = []
                            st["selected"]   = None
                            st["hints"]      = []
                            st["winner"] = check_winner(st["board"], st["steps"])
                            if not st["winner"]:
                                st["turn"]        = -1
                                st["ai_thinking"] = True
                                st["ai_delay"]    = pygame.time.get_ticks()
                    # Клик мимо — игнорируем
                    continue

                # ── Обычный выбор ────────────────────────
                all_moves = get_moves(st["board"], 1)
                is_jump_phase = any(len(m[2][0]) == 4 for m in all_moves) if all_moves else False

                # Клик на подсказку (цель хода)
                clicked_hint = next(
                    (m for m in st["hints"] if m[2][0][0]==r and m[2][0][1]==c),
                    None
                )
                if clicked_hint:
                    sr, sc, chain = clicked_hint
                    if len(chain) == 1 and len(chain[0]) == 2:
                        # Простой ход — применяем сразу
                        st["board"], _ = do_move(st["board"], clicked_hint)
                        st["steps"]   += 1
                        st["selected"] = None
                        st["hints"]    = []
                        st["winner"]   = check_winner(st["board"], st["steps"])
                        if not st["winner"]:
                            st["turn"]        = -1
                            st["ai_thinking"] = True
                            st["ai_delay"]    = pygame.time.get_ticks()
                    else:
                        # Взятие — запускаем пошаговую цепочку
                        from checkers_engine import _single_jumps
                        b = st["board"].copy()
                        nxt = _single_jumps(b, sr, sc, exclude=set())
                        st["chain_pos"]    = (sr, sc)
                        st["chain_board"]  = b
                        st["chain_killed"] = set()
                        st["chain_hints"]  = nxt
                        st["selected"]     = (sr, sc)
                        st["hints"]        = []
                    continue

                # Клик на свою шашку
                if np.sign(st["board"][r][c]) == 1:
                    pm = [m for m in all_moves if m[0]==r and m[1]==c]
                    st["selected"] = (r, c) if pm else None
                    st["hints"]    = pm
                else:
                    st["selected"] = None
                    st["hints"]    = []

        # ── Ход AI ──────────────────────────────────
        if st["ai_thinking"] and pygame.time.get_ticks() - st["ai_delay"] >= 600:
            move = ai_choose(st["board"])
            if move:
                st["board"], _ = do_move(st["board"], move)
                st["steps"]   += 1
            st["winner"]      = check_winner(st["board"], st["steps"])
            st["turn"]        = 1
            st["ai_thinking"] = False

        draw_all(
            st["board"], st["selected"], st["hints"],
            st["winner"], st["steps"], st["ai_thinking"], st["turn"],
            st["chain_pos"], st["chain_hints"]
        )


if __name__ == "__main__":
    main()