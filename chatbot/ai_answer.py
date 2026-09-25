from dotenv import load_dotenv
import openai
import os

load_dotenv()

LLAMA_URL = os.environ["LLAMA_URL"]

client = openai.OpenAI(base_url=LLAMA_URL, api_key="no-key-required")

def ai_answer(answer) -> str:
    completion = client.chat.completions.create(
    model="Qwen/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M",
    max_tokens=1700,
    temperature=1,
    top_p=0.8,
    extra_body={
        "top_k": 20,
        "min_p": 0.0,
        "repetition_penalty": 1.1,  # substitui o presence_penalty agressivo
    },
    messages=[
        {"role": "user", "content": answer},
    ],
)

    choice = completion.choices[0]
    if choice.finish_reason == "length":
        deu_errado = "Bell do código: ele provavelmente ficou repetindo as mesmas palavras e excedeu o limite de tokens que eu coloquei"
        print(deu_errado)

    return (choice.message.content or deu_errado).strip()

