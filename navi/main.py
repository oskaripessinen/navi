import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_API_KEY")
)

completion = client.chat.completions.create(
    model="Qwen/Qwen3-Next-80B-A3B-Instruct:novita",
    messages=[
        {
            "role": "user",
            "content": "Hi"
        }
    ],
)

print(completion.choices[0].message)