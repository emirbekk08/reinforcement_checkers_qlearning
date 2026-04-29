import streamlit as st
import pickle
import os

st.set_page_config(page_title="Шашки Q-Learning", page_icon="♟️", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a0a00, #3d1f00); color: white; }
    .card  { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,180,0,0.3);
             border-radius: 12px; padding: 20px; margin: 10px 0; }
    .card h3 { color: #ffaa00; }
    .card p  { color: #dddddd; }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown("<h1 style='text-align:center;color:white'>♟️ Шашки 8x8 — Q-Learning</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#aaa'>Reinforcement Learning проект</p>", unsafe_allow_html=True)

st.divider()

# Датасет / среда
st.header("🎯 Среда")
c1, c2, c3 = st.columns(3)
c1.metric("Игра",            "Шашки 8x8")
c2.metric("Шашек у каждого", "12")
c3.metric("Эпизодов",        "30,000")

st.divider()

# Что такое Reinforcement Learning
st.header("🧠 Что такое Reinforcement Learning?")
st.markdown("""
<div class="card">
<p>
Reinforcement Learning — это обучение через <b style="color:#ffaa00">награды и наказания</b>.<br><br>
Агент делает ходы и получает:
<ul>
<li>✅ <b>+10</b> — победил (съел все шашки противника)</li>
<li>❌ <b>-10</b> — проиграл (потерял все свои шашки)</li>
<li>⬜ <b>0</b>  — обычный ход</li>
</ul>
После 30,000 игр агент научился играть лучше!
</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Описание проекта
st.header("📋 Описание проекта")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="card">
    <h3>🎯 Цель</h3>
    <p>Обучить AI агента играть в шашки 8x8 используя Q-Learning алгоритм без готовых ответов.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="card">
    <h3>⚙️ Алгоритм Q-Learning</h3>
    <p>Агент строит таблицу Q[состояние][ход] и выбирает ход с максимальным значением.
    Поддерживает дамки ♛ и множественные прыжки.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# График обучения
st.header("📈 График обучения")
if os.path.exists("static/training.png"):
    st.image("static/training.png", caption="Процент побед AI по ходу обучения")
else:
    st.warning("Сначала запусти train.py чтобы увидеть график!")

st.divider()

# Результат обучения
st.header("📊 Результат обучения")
try:
    with open("model/q_table.pkl", "rb") as f:
        q_table = pickle.load(f)
    c1, c2, c3 = st.columns(3)
    c1.metric("Состояний изучено", f"{len(q_table):,}")
    c2.metric("Игр сыграно",       "30,000")
    c3.metric("Лучший результат",  "~53%")
    st.success("✅ Модель загружена!")
except:
    st.warning("Запусти train.py сначала!")

st.divider()

# Правила
st.header("📜 Правила")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="card">
    <h3>🔴 AI (красные)</h3>
    <p>
    • Ходит снизу вверх<br>
    • Достигает верха → становится дамкой ♛<br>
    • Дамка ходит в любую сторону на много клеток<br>
    • Обязан бить если есть возможность
    </p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="card">
    <h3>⚫ ПК (чёрные)</h3>
    <p>
    • Ходит сверху вниз<br>
    • Достигает низа → становится дамкой ♛<br>
    • Играет случайными ходами<br>
    • Тоже обязан бить
    </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Как запустить
st.header("🎮 Как запустить игру")
st.code("python play.py", language="bash")
st.markdown("""
<div class="card">
<p>
🔴 AI ходит автоматически по Q-таблице<br>
⚫ ПК ходит случайно<br>
♛ Золотой круг = дамка<br>
⌨️ <b>R</b> = перезапустить игру
</p>
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown("<p style='text-align:center;color:#666'>Шашки 8x8 · Q-Learning · Reinforcement Learning</p>",
            unsafe_allow_html=True)