# ============================================================================
# PERPLEXITY CLONE - SISTEMA DE PESQUISA INTELIGENTE COM GROQ
# ============================================================================
# Este sistema implementa um clone do Perplexity usando LangGraph e Groq LLMs
# para realizar pesquisas inteligentes na web com múltiplas queries paralelas
# e síntese final das informações encontradas.
# ============================================================================

# Importações principais
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver
from time import time
import streamlit as st

# Módulos locais
from schemas import *    # Definições de estado e modelos de dados
from prompts import *    # Templates de prompts para LLMs
from utils import *      # Utilitários para pesquisa web (Tavily)

# Carregamento de variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# CONFIGURAÇÃO DAS LLMs GROQ
# ============================================================================
# Utilizamos dois modelos Groq diferentes para otimizar performance e custo:
# - Modelo rápido (8B) para processamento de queries e resumos
# - Modelo robusto (70B) para síntese final e raciocínio complexo
# ============================================================================

# LLM principal - Modelo rápido para tarefas de processamento
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # Modelo otimizado para velocidade
    temperature=0.1,                # Baixa criatividade para consistência
    max_tokens=None,               # Sem limite específico de tokens
    timeout=None,                  # Sem timeout específico
    max_retries=2,                 # Retry automático em caso de falha
)

# LLM para raciocínio final - Modelo robusto para síntese complexa
reasoning_llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Modelo mais poderoso para raciocínio
    temperature=0.1,                   # Baixa criatividade para precisão
    max_tokens=None,                   # Sem limite específico de tokens
    timeout=None,                      # Sem timeout específico
    max_retries=2,                     # Retry automático em caso de falha
)

# ============================================================================
# FUNÇÕES DO GRAFO DE PESQUISA
# ============================================================================

def build_first_queries(state: ReportState):
    """
    ETAPA 1: GERAÇÃO DE QUERIES DE PESQUISA
    
    Analisa a pergunta do usuário e gera múltiplas queries de pesquisa
    otimizadas para cobrir diferentes aspectos da questão.
    
    Args:
        state (ReportState): Estado contendo a pergunta do usuário
        
    Returns:
        dict: Dicionário com lista de queries geradas
    """
    class QueryList(BaseModel):
        queries: List[str]
        
    user_input = state['user_input']

    # Formatar prompt com a pergunta do usuário
    prompt = build_queries.format(user_input=user_input)
    
    # Gerar queries usando LLM rápida (8B) com saída estruturada
    query_llm = llm.with_structured_output(QueryList)
    result = query_llm.invoke(prompt)

    return {"queries": result.queries}

def spawn_researchers(state: ReportState):
    """
    ETAPA 2: DISTRIBUIÇÃO DE TAREFAS DE PESQUISA
    
    Cria tarefas paralelas de pesquisa web para cada query gerada,
    permitindo processamento simultâneo e otimização de tempo.
    
    Args:
        state (ReportState): Estado contendo as queries geradas
        
    Returns:
        List[Send]: Lista de tarefas Send para execução paralela
    """
    return [Send("single_search", {"query": query, "user_input": state['user_input']}) 
            for query in state['queries']]

def single_search(data: dict):
    """
    ETAPA 3: EXECUÇÃO DE PESQUISA INDIVIDUAL
    
    Executa uma pesquisa web individual usando a API Tavily,
    processa o conteúdo retornado e gera um resumo focado
    na pergunta original do usuário.
    
    CARACTERÍSTICAS:
    - Usa include_raw_content=True para obter conteúdo completo
    - Implementa fallback robusto (raw_content -> content -> snippet)
    - Limita conteúdo a 1500 caracteres para controle de tokens
    - Tratamento de exceções para limites de API
    
    Args:
        data (dict): Dicionário contendo 'query' e 'user_input'
        
    Returns:
        dict: Dicionário com 'queries_results' contendo lista de QueryResult
    """
    # Extrair parâmetros do dicionário de entrada
    query = data["query"]
    user_input = data["user_input"]
    
    try:
        # PESQUISA WEB: Inicializar cliente Tavily e buscar com conteúdo completo
        tavily_client = TavilyClient()
        results = tavily_client.search(query, 
                             max_results=1, 
                             include_raw_content=True)  # Habilita conteúdo completo da página

        query_results = []
        
        # PROCESSAMENTO DE RESULTADOS: Iterar sobre cada resultado encontrado
        for result in results["results"]:
            url = result["url"]
            title = result["title"]
            
            # ESTRATÉGIA DE FALLBACK: Priorizar raw_content, depois content
            content = result.get("content", "")
            raw_content = result.get("raw_content", content)
            
            if raw_content:
                # CONTROLE DE TOKENS: Limitar conteúdo para evitar erro 413 (máximo 1500 caracteres)
                if len(raw_content) > 1500:
                    raw_content = raw_content[:1500] + "..."
                
                # GERAÇÃO DE RESUMO: Usar LLM para processar conteúdo focado na pergunta
                prompt = resume_search.format(user_input=user_input,
                                            search_results=raw_content)

                llm_result = llm.invoke(prompt)
                query_results.append(QueryResult(title=title,
                                        url=url,
                                        resume=llm_result.content))
            else:
                # FALLBACK: Usar snippet básico quando não há conteúdo completo
                query_results.append(QueryResult(title=title,
                                        url=url,
                                        resume=content or "Conteúdo não disponível"))
                
    except Exception as e:
        # TRATAMENTO DE ERRO: Capturar limites de API, falhas de conexão, etc.
        print(f"Erro na busca: {e}")
        # Fallback em caso de erro: retorna resultado básico para continuidade
        query_results = [QueryResult(title=f"Busca: {query}",
                                   url="#",
                                   resume=f"Erro ao buscar informações sobre: {query}")]
    
    return {"queries_results": query_results}

def final_writer(state: ReportState):
    """
    ETAPA 4: SÍNTESE FINAL E GERAÇÃO DE RESPOSTA
    
    Combina todos os resultados de pesquisa individuais em uma
    resposta coerente e abrangente usando o modelo LLM mais robusto.
    
    PROCESSO:
    1. Compila resumos de todas as queries executadas
    2. Limita conteúdo individual para controle de tokens
    3. Formata referências numeradas para citação
    4. Usa LLM 70B para síntese final de alta qualidade
    
    Args:
        state (ReportState): Estado contendo todos os resultados de pesquisa
        
    Returns:
        dict: Resposta final com referências formatadas
    """
    # COMPILAÇÃO DE DADOS: Agregar todos os resumos e referências
    search_results = ""
    references = ""
    
    for i, result in enumerate(state['queries_results']):
        # CONTROLE DE TOKENS: Limitar cada resumo individual (300 chars)
        resume_content = result.resume
        if len(resume_content) > 300:
            resume_content = resume_content[:300] + "..."
            
        # FORMATAÇÃO: Estruturar resultados numerados para o prompt
        search_results += f"[{i+1}] {result.title}\n{resume_content}\n\n"
        references += f"[{i+1}] - [{result.title}]({result.url})\n"
    
    # PREPARAÇÃO DO PROMPT: Consolidar pergunta e resultados
    prompt = build_final_response.format(user_input=state['user_input'],
                                    search_results=search_results)

    # SÍNTESE FINAL: Usar LLM robusto (70B) para raciocínio complexo
    llm_result = reasoning_llm.invoke(prompt)

    print(llm_result)
    # FORMATAÇÃO FINAL: Combinar resposta com referências
    final_response = llm_result.content + "\n\n References:\n" + references

    return {"final_response": final_response}

# ============================================================================
# CONSTRUÇÃO DO GRAFO LANGGRAPH
# ============================================================================
# O grafo define o fluxo de execução do sistema de pesquisa:
# START -> build_first_queries -> spawn_researchers -> single_search -> final_writer -> END
# ============================================================================

# Inicializar grafo com o estado ReportState
builder = StateGraph(ReportState)

# ADIÇÃO DE NÓS: Cada função representa uma etapa do processo
builder.add_node("build_first_queries", build_first_queries)  # Gera queries de pesquisa
builder.add_node("single_search", single_search)            # Executa pesquisas individuais
builder.add_node("final_writer", final_writer)              # Sintetiza resposta final

# DEFINIÇÃO DE FLUXO: Conectar nós com lógica condicional para paralelização
builder.add_edge(START, "build_first_queries")               # Início: gerar queries
builder.add_conditional_edges("build_first_queries",         # Distribuir pesquisas paralelas
                              spawn_researchers,              # Função que cria tarefas Send
                              ["single_search"])              # Destino das tarefas paralelas
builder.add_edge("single_search", "final_writer")           # Compilar resultados
builder.add_edge("final_writer", END)                       # Finalizar processo

# COMPILAÇÃO: Criar aplicação executável
graph = builder.compile()

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================
# Interface web para interação com o sistema de pesquisa inteligente
# Permite entrada de perguntas e exibição de respostas com referências
# ============================================================================

if __name__ == "__main__":
    # CONFIGURAÇÃO DA INTERFACE: Título e campo de entrada
    st.title("🌎 Local Perplexity")
    user_input = st.text_input("Qual a sua pergunta?", 
                               value="How is the process of building a LLM?")

    # PROCESSAMENTO DA PESQUISA: Executar quando botão é pressionado
    if st.button("Pesquisar"):
        # INDICADOR DE PROGRESSO: Mostrar status durante execução
        with st.status("Gerando resposta"):
            # EXECUÇÃO DO GRAFO: Stream com modo debug para acompanhamento
            for output in graph.stream({"user_input": user_input},
                                        stream_mode="debug"     # Modo debug para logs detalhados
                                        # stream_mode="messages" # Alternativa: modo mensagens
                                        ):
                # LOGS DE PROGRESSO: Mostrar etapas sendo executadas
                if output["type"] == "task_result":
                    st.write(f"Running {output['payload']['name']}")
                    st.write(output)
        
        # EXTRAÇÃO DA RESPOSTA: Obter resultado final do último output
        response = output["payload"]["result"][0][1]
        
        # PROCESSAMENTO DE RESPOSTA: Verificar se contém tags de pensamento (deepseek-style)
        if "</think>" in response:
            # SEPARAÇÃO: Dividir pensamento e resposta final
            think_str = response.split("</think>")[0]
            final_response = response.split("</think>")[1]

            # EXIBIÇÃO: Mostrar reflexão em expander colapsável
            with st.expander("🧠 Reflexão", expanded=False):
                st.write(think_str)
            st.write(final_response)
        else:
            # EXIBIÇÃO DIRETA: Mostrar resposta sem processamento adicional
            st.write(response)
