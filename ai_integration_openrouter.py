import openai
from config import OPENROUTER_API_KEY

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1", 
    api_key=OPENROUTER_API_KEY
)

def generate_profession_recommendations(subjects):
    prompt = f"""
    Пользователь выбрал следующие любимые школьные предметы: {', '.join(subjects)}.
    Предложи ТОП-2 профессии, которые ему подойдут. Для каждой профессии укажи:
    - Название
    - Описание (1–2 предложения)
    - Ключевые навыки
    - Зарплата: Junior / Middle / Senior
    - Где учиться: вуз или курсы

    Формат вывода: структурированный текст на русском языке без markdown.
    Пример формата:
    
    1. Литературный редактор
       - Описание: ...
       - Ключевые навыки: ...
       - Зарплата: ...
       - Где учиться: ...
    """

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Ошибка при обращении к AI модели: {e}")
        return None

def parse_ai_response(text):
    import re

    if not text or not isinstance(text, str):  # Защита от None
        return []

    professions = []
    blocks = re.split(r'\d+\.\s', text)[1:]

    for block in blocks:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if not lines:
            continue
        name = lines[0]

        data = {
            "name": name,
            "description": "",
            "skills": [],
            "salary": "",
            "education": [],
        }

        for line in lines[1:]:
            if line.startswith("- Описание") or line.startswith("Описание"):
                data["description"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Ключевые навыки") or line.startswith("Ключевые навыки"):
                skills = line.split(":", 1)[1].strip()
                data["skills"] = [s.strip() for s in skills.split(",")]
            elif line.startswith("- Зарплата"):
                data["salary"] = line.split(":", 1)[1].strip()
            elif line.startswith("- Где учиться") or line.startswith("Где учиться"):
                education = line.split(":", 1)[1].strip()
                data["education"] = [e.strip() for e in education.split(",")]

        professions.append(data)

    return professions