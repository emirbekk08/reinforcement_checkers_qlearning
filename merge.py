import pickle
import os

print("Объединение знаний AI и AI2...")

# Загружаем обе Q-таблицы
with open("model/q_ai.pkl", "rb") as f:
    q_ai = pickle.load(f)
with open("model/q_ai2.pkl", "rb") as f:
    q_ai2 = pickle.load(f)

print(f"AI  знает: {len(q_ai):,} позиций")
print(f"AI2 знает: {len(q_ai2):,} позиций")

# Объединяем
q_merged = dict(q_ai)  # начинаем с AI

for key, value in q_ai2.items():
    if key in q_merged:
        # Оба знают эту позицию → берём лучшее (максимум)
        q_merged[key] = max(q_merged[key], value)
    else:
        # Только AI2 знает → добавляем
        q_merged[key] = value

print(f"\nОбъединённая таблица: {len(q_merged):,} позиций")
print(f"Прирост знаний: +{len(q_merged) - len(q_ai):,} позиций от AI2")

# Сохраняем объединённую модель
with open("model/q_merged.pkl", "wb") as f:
    pickle.dump(q_merged, f)

print("\n✅ Объединённая модель сохранена → model/q_merged.pkl")
print("Теперь запусти play.py — будешь играть против объединённого AI!")