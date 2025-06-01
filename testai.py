import openai
from config import OPENROUTER_API_KEY

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1", 
    api_key=OPENROUTER_API_KEY
)

try:
    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct:free",
        messages=[{"role": "user", "content": "Привет, кто ты?"}],
        max_tokens=50
    )
    print("✅ Ответ от AI:", response.choices[0].message.content)
except Exception as e:
    print("❌ Ошибка при обращении к AI:", e)