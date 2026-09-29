from dotenv import load_dotenv
import openai
import os

load_dotenv()

LLAMA_URL = os.environ["LLAMA_URL"]
llm = openai.OpenAI(base_url=LLAMA_URL, api_key="no-key-required")

SYSTEM_PROMPT = """
Escreva UMA pergunta absurda e caótica em português do Brasil.

A pergunta deve misturar coisas que não têm nada a ver, tratar o impossível como se fosse normal e ter um detalhe sem sentido no meio. Escolha assuntos totalmente aleatórios a cada vez: objetos, animais, comidas, lugares, números, burocracia, natureza, tecnologia, parentes.

Exemplos do estilo (NÃO copie, invente outra):
Por que a geladeira do meu tio ainda espera o resultado de 1998?
Qual a taxa de juros do boleto que a Lua pagou com o sapato?
O buraco negro da padaria precisa de CPF pra comprar pão francês?
Quantos megas de wifi um elefante gasta pra esquecer a terça?

Regras:
- Uma frase só, curta, terminando em "?".
- Responda SOMENTE com a pergunta. Sem introdução, sem explicação, sem aspas, sem "Pergunta:".
- Nunca repita os exemplos nem o tema deles.
"""


def history_resize(history, maxmessages=20):
    return history[-maxmessages:]


def ai_msg(history):
    """history: lista de perguntas já geradas (alterada no lugar).
    Retorna (pergunta, resposta)."""
    system = SYSTEM_PROMPT
    if history:
        anteriores = "\n".join(f"- {q}" for q in history)
        system += (
            "\n\nPerguntas já feitas (não repita tema nem estrutura):\n"
            f"{anteriores}"
        )

    gen = llm.chat.completions.create(
        model="unsloth/Qwen3.5-0.8B-GGUF:Q4_K_XL",
        max_tokens=700,
        temperature=0.7,
        top_p=0.8,
        presence_penalty=1.5,
        extra_body={
            "top_k": 20,
            "min_p": 0.0,
            "chat_template_kwargs": {"enable_thinking": False},
        },
        messages=[{"role": "user", "content": system}],
    ).choices[0]

    pergunta = (gen.message.content or "").strip()
    if not pergunta:
        return "", ""

    burra = llm.chat.completions.create(
        model="Qwen/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M",
        max_tokens=700,
        temperature=1.3,
        top_p=0.95,
        extra_body={
            "top_k": 100,
            "min_p": 0.02,
            "repeat_penalty": 1.15,  # nome usado pelo llama.cpp
        },
        messages=[{"role": "user", "content": pergunta}],
    ).choices[0]

    resposta = (burra.message.content or "").strip()

    if gen.finish_reason == "length" or burra.finish_reason == "length":
        print(
            "Bell do código: ele provavelmente ficou repetindo as mesmas "
            "palavras e excedeu o limite de tokens que eu coloquei"
        )

    history.append(pergunta)
    history[:] = history_resize(history)

    return pergunta, resposta