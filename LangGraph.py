from CND_IA import cnd_divida_ativa
from config_IA import IADividaAtiva
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langsmith import traceable
from typing import TypedDict, Annotated

class EstadoRPA(TypedDict):
    etapa: str
    messages: Annotated[list, add_messages]

@traceable
def etapa_download(state: EstadoRPA):
    print("[LangGraph] Baixando certidão...")
    cnd_divida_ativa()
    state["etapa"] = "download_concluido"
    return state

@traceable
def etapa_extracao(state: EstadoRPA):
    state["etapa"] = "extracao_concluida"
    return state

graph = StateGraph(EstadoRPA)
graph.add_node("download", etapa_download)
graph.add_node("extracao", etapa_extracao)
graph.add_edge(START, "download")
graph.add_edge("download", "extracao")
graph.add_edge("extracao", END)

app = graph.compile()

if __name__ == "__main__":
    app.invoke({"messages": [{"role": "user", "content": "Iniciar processo"}]})
