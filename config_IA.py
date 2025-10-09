from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "CND_Divida_Ativa"

class IADividaAtiva:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("CHAVE_OPENIA"))
        self.model = "gpt-4o-mini"

    @traceable
    def extrair_informacoes(self, texto_pdf):
        perguntas = [
            "Qual é a data de emissão da certidão?",
            "Qual é o horário da emissão?",
            "Qual é a validade da certidão?"
        ]
        respostas = {}

        for pergunta in perguntas:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente que extrai dados de PDFs fiscais."},
                    {"role": "user", "content": f"Texto: {texto_pdf}\nPergunta: {pergunta}"}
                ]
            )
            respostas[pergunta] = completion.choices[0].message.content.strip()

        return respostas
