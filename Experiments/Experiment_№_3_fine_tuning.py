# -*- coding: utf-8 -*-
"""Experiment № 3. Fine-tuning.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yyj_J11-FpOcE859WwXT8ciSkxNmCSsG
"""

! pip install langchain openai chromadb tiktoken

import os
import pandas as pd
import openai
from openai import OpenAI
import json

client = OpenAI(
    api_key = "***" # здесь вводить ключ
)

# Загрузка файла
df = pd.read_csv('/content/itkin_data_rm.csv')
# Выбор столбцов
df = df[['lemma', 'pos', 'morphemic_structure']]
# Вывод фрагмента датасета
df.head()

# Функция для создания формата сообщений
def create_message(row):
    user_message = f"Разбери на морфемы слово '{row['lemma']}')?"
    assistant_message = (f"Лемма: {row['lemma']}\n"
                         f"Морфемная структура: {row['morphemic_structure']}")
    return {
        "messages": [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
    }

# Преобразование в формат json
messages = df.apply(create_message, axis=1).tolist()

# Сохранение в файл
with open('/content/itkin-dataset.jsonl', 'w', encoding='utf-8') as f:
    for message in messages:
        f.write(json.dumps(message, ensure_ascii=False) + '\n')

print("Датасет успешно преобразован в формат JSON Lines.")

# создание айдишника
response = client.files.create(
    file=open("/content/itkin-dataset.jsonl", "rb"),
    purpose='fine-tune'
)

file_id = response.id
print(f"File ID: {file_id}")

# Запуск процесса fine-tuning
response = client.fine_tuning.jobs.create(
  training_file=file_id,
  model='gpt-3.5-turbo'
)

model_id = response.id
print(f"File ID: {model_id}")

# Идентификатор задания fine-tuning
job_id = 'ftjob-2S5aAAoiZVU1WyYVLK3AXaZj'

# Получение статуса задания
response = client.fine_tuning.jobs.retrieve(job_id)
print(response)

# Если fine-tuning завершен, получить идентификатор модели
if response.status == 'succeeded':
    model_id = response.fine_tuned_model
    print(f"Fine-tuned model ID: {model_id}")
else:
    print(f"Current status: {response.status}")

# Пример конкретного запроса
prompt = "Разбери на морфемы слово 'снежный'"

response = client.chat.completions.create(
    model=model_id,
    messages=[{"role": "user", "content": prompt}],
)

# Вывод результата
print(response.choices[0].message.content)

# Список слов для разбора
list_words_itkin = ['окружность', 'абажур', 'чужеземец', 'прибавление', 'рефлекс', 'чулочки', 'шантажистка',
                    'шар', 'рукавицы', 'посланница', 'аббатский', 'грифельный', 'двигательный', 'ерундовский',
                    'кожаный', 'барсучий', 'мерзопакостный', 'меньший', 'мифический', 'обжаренный', 'вычистить',
                    'гвоздить', 'гнездоваться', 'дезорганизовать', 'докроить', 'жадничать', 'надпарывать',
                    'освобождаться', 'ослаблять', 'перетряхнуть', 'аварийно', 'бобриком', 'вдобавок', 'вкратце',
                    'гуськом', 'добела', 'живьем', 'исподнизу', 'по-испански', 'по-другому']

# Список слов для разбора
list_words_KE = ['бездуховность', 'абажур', 'авианосец', 'напыление', 'рефлекс', 'чулочки', 'шантажистка',
                    'ячменек', 'рукавицы', 'подберезник', 'аббатский', 'грифельный', 'рекомендательный', 'банковский',
                    'гаданый', 'барсучий', 'мерзопакостный', 'меньший', 'мифический', 'обжаренный', 'вычистить',
                    'гвоздить', 'гнездоваться', 'дезорганизовать', 'докроить', 'жадничать', 'надпарывать',
                    'освобождаться', 'ослаблять', 'перетряхнуть', 'жалко', 'бобриком', 'вдобавок', 'вкратце',
                    'гуськом', 'добела', 'живьем', 'потемну', 'по-испански', 'по-другому']

# Список слов для разбора
list_words_tikhonov = ['бездуховность', 'абажур', 'авианосец', 'напыление', 'рефлекс', 'чулочки', 'шантажистка',
                    'шар', 'рукавицы', 'подберезник', 'аббатский', 'грифельный', 'рекомендательный', 'банковский',
                    'гаданый', 'барсучий', 'алмазоносный', 'затекший', 'мифический', 'обжаренный', 'выметить',
                    'гвоздить', 'гнездоваться', 'дезорганизовать', 'докроить', 'жадничать', 'излизывать',
                    'освобождаться', 'ослаблять', 'перетряхнуть', 'жалко', 'напролом', 'вдобавок', 'вкратце',
                    'гуськом', 'добела', 'живьем', 'потемну', 'по-испански', 'по-другому']

model_id = '***' # ID модели

words = list_words_KE

# Функция для разбора слова на морфемы
def get_morphemes(word):
    prompt = f"Разбери на морфемы слово '{word}'"
    response = client.chat.completions.create(
    model=model_id,
    messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

# Список для хранения результатов
results = []

# Обработка каждого слова
for word in words:
    morphemes = get_morphemes(word)
    results.append({"word": word, "morphemes": morphemes})

# Создание датасета из результатов
df = pd.DataFrame(results)

# Сохранение датасета
df.to_csv("morphemes_dataset_40_KE.csv", index=False)

# Вывод фрагмента датасета
df.head()