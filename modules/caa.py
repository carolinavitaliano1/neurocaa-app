import os
import time
from openai import OpenAI, RateLimitError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_palavras_caa(texto):
    prompt = f"""
    Transforme a frase abaixo em palavras isoladas para Comunicação Alternativa.
    Mantenha verbos, artigos e conectivos simples.
    Retorne somente uma lista separada por vírgulas.

    Frase: {texto}
    """

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return [p.strip().lower() for p in resposta.choices[0].message.content.split(",")]

    except RateLimitError:
        time.sleep(3)
        return []
