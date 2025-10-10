from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langsmith import traceable
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "CND_Divida_Ativa"

class IADividaAtiva:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("CHAVE_OPENIA"),
            temperature=0)

    @traceable
    def extrair_informacoes(self, texto_pdf):
        perguntas = [
            "Qual é a data de emissão da certidão?",
            "Qual é o horário da emissão?",
            "Qual é a validade da certidão?"]
        respostas = {}

        for pergunta in perguntas:
            mensagens = [
                SystemMessage(content="Você é um assistente que extrai dados de PDFs fiscais."),
                HumanMessage(content=f"Texto: {texto_pdf}\nPergunta: {pergunta}")]

            resposta = self.llm.invoke(mensagens)
            respostas[pergunta] = resposta.content.strip()

        return respostas
