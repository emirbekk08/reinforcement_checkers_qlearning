"""
train.py — обучение двух AI методом Q-learning.
Использует checkers_engine.py (цепочки взятий, дамка на всю диагональ).
После обучения сохраняет q_ai.pkl и q_ai2.pkl.
Запусти merge.py чтобы объединить их в q_merged.pkl.
"""

import numpy as np
import pickle
import os
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from checkers_engine import make_board, get_moves, do_move, check_winner, get_state

# ──────────────────────────────────────────
#  ПАРАМЕТРЫ
# ──────────────────────────────────────────
EPISODES   = 60000
LR         = 0.2      # learning rate
GAMMA      = 0.9      # discount
EPS_START  = 1.0
EPS_MIN    = 0.05
EPS_DECAY  = 0.00003

# Награды
R_TAKE     =  5       # за каждую съеденную шашку
R_KING     = 10       # за превращение в дамку
R_WIN      = 50
R_LOSE     = -50

# ──────────────────────────────────────────
#  Q-ТАБЛИЦА
# ──────────────────────────────────────────
def make_q():
    return {}

def q_get(Q, state, move):
    return Q.get((state, str(move)), 0.0)

def q_update(Q, state, move, reward, next_state, next_moves):
    old  = q_get(Q, state, move)
    best = max((q_get(Q, next_state, m) for m in next_moves), default=0.0)
    Q[(state, str(move))] = old + LR * (reward + GAMMA * best - old)


# ──────────────────────────────────────────
#  ОДИН ЭПИЗОД
# ──────────────────────────────────────────
def run_episode(Q1, Q2, epsilon):
    board  = make_board()
    steps  = 0
    done   = False
    total  = [0, 0]    # суммарная награда Q1 и Q2

    while not done:
        for player, Q in [(1, Q1), (-1, Q2)]:
            moves = get_moves(board, player)
            if not moves:
                done = True
                break

            state = get_state(board)

            # Epsilon-greedy
            if random.random() < epsilon:
                move = random.choice(moves)
            else:
                move = max(moves, key=lambda m: q_get(Q, state, m))

            prev_red  = int(np.sum(board > 0))
            prev_gray = int(np.sum(board < 0))
            prev_kings_r = int(np.sum(board == 2))
            prev_kings_g = int(np.sum(board == -2))

            board, taken = do_move(board, move)
            steps += 1

            # Считаем награду
            reward = taken * R_TAKE
            if player == 1:
                new_kings = int(np.sum(board == 2)) - prev_kings_r
            else:
                new_kings = int(np.sum(board == -2)) - prev_kings_g
            reward += new_kings * R_KING

            winner = check_winner(board, steps)
            if winner is not None:
                if winner == player: reward += R_WIN
                elif winner == 0:    reward += 0
                else:                reward += R_LOSE
                done = True

            next_moves = get_moves(board, player) if not done else []
            next_state = get_state(board)
            q_update(Q, state, move, reward, next_state, next_moves)

            idx = 0 if player == 1 else 1
            total[idx] += reward

            if done:
                break

    return total


# ──────────────────────────────────────────
#  ОСНОВНОЙ ЦИКЛ
# ──────────────────────────────────────────
os.makedirs("model",  exist_ok=True)
os.makedirs("static", exist_ok=True)

Q1 = make_q()
Q2 = make_q()
epsilon = EPS_START

history_r = []   # история наград красных
history_g = []

print(f"Запуск обучения: {EPISODES} эпизодов...")

for ep in range(1, EPISODES + 1):
    rewards = run_episode(Q1, Q2, epsilon)
    history_r.append(rewards[0])
    history_g.append(rewards[1])
    epsilon = max(EPS_MIN, epsilon - EPS_DECAY)

    if ep % 5000 == 0:
        print(f"Эп {ep:>6}/{EPISODES}  |  Q1: {len(Q1):,}  Q2: {len(Q2):,}  ε={epsilon:.3f}")

# ──────────────────────────────────────────
#  СОХРАНЕНИЕ
# ──────────────────────────────────────────
with open("model/q_ai.pkl",  "wb") as f: pickle.dump(Q1, f)
with open("model/q_ai2.pkl", "wb") as f: pickle.dump(Q2, f)
print(f"\nСохранено: q_ai.pkl ({len(Q1):,})  q_ai2.pkl ({len(Q2):,})")
print("Запусти merge.py → затем play.py")

# ──────────────────────────────────────────
#  ГРАФИК
# ──────────────────────────────────────────
window = 500
def smooth(arr):
    return [np.mean(arr[max(0,i-window):i+1]) for i in range(len(arr))]

plt.figure(figsize=(11, 4))
plt.plot(smooth(history_r), color="crimson",  label="Красные (AI1)")
plt.plot(smooth(history_g), color="steelblue",label="Серые   (AI2)")
plt.title("Прогресс обучения (средняя награда)")
plt.xlabel("Эпизод"); plt.ylabel("Награда")
plt.legend(); plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig("static/training_graph.png")
plt.savefig("static/training.png")
print("График сохранён → static/training_graph.png")