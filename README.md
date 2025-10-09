<h1 style="text-align: left; font-size: 42px;">🤖 Automação RPA Inteligente</h1>
<h3 style="text-align: left;">Integrando Selenium + IA (LangChain / LangGraph / LangSmith)</h3>

Projeto de automação fiscal que combina **RPA (Selenium)**, **LangChain (LangSmith + LangGraph)** e **IA generativa (OpenAI)**  
para executar e monitorar automaticamente a emissão e leitura de **Certidões de Dívida Ativa (CND)** do portal.

---

## 🧠 Arquitetura Geral

Este projeto integra **três camadas principais**:

| Camada | Descrição | Ferramentas |
|--------|------------|-------------|
| 🧩 **1. IA Cognitiva (LLM)** | Extrai informações fiscais diretamente de PDFs (ex: data, validade, horário de emissão) | `OpenAI GPT-4o-mini` + `LangSmith` |
| ⚙️ **2. Automação RPA** | Acessa o site da Dívida Ativa, resolve CAPTCHA, baixa e organiza o PDF da certidão | `Selenium`, `Anti-Captcha API`, `pdfplumber` |
| 🔄 **3. Orquestração Inteligente** | Define o fluxo de execução via grafo de estados com rastreamento detalhado | `LangGraph` + `LangSmith` |

---

## 🗂️ Estrutura do Projeto

langchain LLM estudos/
│
├── main.py → Implementa a classe IADividaAtiva (IA que extrai informações dos PDFs)
├── Divida_Ativa.py → Robô Selenium com AntiCaptcha + IA integrada
└── LangGraph.py → Orquestrador que conecta todo o fluxo via LangGraph

---

## ⚙️ Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seuusuario/nome-do-repo.git
   cd nome-do-repo
   ```
   
   ---
   
2. Crie e ative um ambiente virtual:
    ```bash
      python -m venv .venv
      .venv\Scripts\activate
   ```

---

3. Instale as dependências:
   ```bash
    pip install -r requirements.txt
   ```

   ---
   
 4. Crie um arquivo .env com suas chaves e parâmetros:
    ```bash
     # OpenAI
    CHAVE_OPENIA=sk-xxxxxx
    # LangSmith
    LANGCHAIN_API_KEY=lsv2_xxxxxx
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_PROJECT=CND_Divida_Ativa
    
    # AntiCaptcha
    CHAVE_API=xxxxxxxxxxxxxxxxx
    
    # Empresa
    CNPJ_BASE=xxxxxxxxxxxxxx
    ```
    
    ---

    Execução
    ```bash 
     python Divida_Ativa.py
    ```
    O script abrirá o site da PGE-SP, resolverá o reCAPTCHA e baixará o PDF da certidão.

    ---
       
    Rodar com orquestração LangGraph
    ```bash
    python LangGraph.py
    ```
    O LangGraph gerencia o fluxo do RPA e registra cada etapa no LangSmith (download, extração, erros, resultados, etc).

    ---

    ## 🔍 Monitoramento (LangSmith)

      Cada execução é registrada automaticamente no LangSmith, permitindo:
    
      Visualizar logs de cada etapa do robô;
      
      Monitorar prompts e respostas da IA;
      
      Medir tempo de execução e desempenho;
      
      Auditar erros e decisões tomadas.
