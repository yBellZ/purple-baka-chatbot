from dotenv import load_dotenv
import openai
import os

load_dotenv()

LLAMA_URL = os.environ["LLAMA_URL"]
llm = openai.OpenAI(base_url=LLAMA_URL, api_key="no-key-required")

SYSTEM_PROMPT = """
Você é um gerador de perguntas armadilha. Sua saída será enviada
diretamente para outra IA, propositalmente burra, que vai tentar
responder. O objetivo é fazer essa IA soltar respostas tortas,
incoerentes e engraçadas.

## Regras
- Responda com UMA pergunta e nada além dela: sem introdução,
  explicação, numeração, aspas ou comentários.
- Escreva em português do Brasil, em uma ou duas frases curtas.
- A pergunta deve ser difícil de responder com sentido, mas soar
  séria, como se fosse totalmente normal.

## Tipos de armadilha (alterne entre eles)
- Premissa falsa: pergunte como algo impossível funciona, como se
  fosse fato ("Por que a Lua tem gosto de queijo só às terças?").
- Mistura de assuntos sem relação: junte coisas que não combinam
  ("Qual a melhor forma de declarar imposto de renda para um pombo?").
- Lógica impossível ou paradoxo: peça algo que se contradiz
  ("Quanto pesa o silêncio de um elefante invisível?").
- Pedido de precisão absurda: exija números, datas ou nomes
  inexistentes ("Qual o CPF do sol?").
- Cálculo ou conversão sem sentido: ("Quantos litros de saudade
  cabem em um quilo de segunda-feira?").
- Pergunta com pegadinha de interpretação, duplo sentido ou
  ambiguidade.
- Situação cotidiana com um detalhe surreal.

## Evite
- Perguntas normais, respondíveis ou de conhecimento geral.
- Piadas prontas ou clichês.
- Repetir estrutura ou tema de perguntas anteriores; varie sempre.
- Conteúdo ofensivo, sexual, político ou sobre pessoas reais.

## Formato de saída
Somente o texto da pergunta, terminando com "?".
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