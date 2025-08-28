# Importações necessárias para o funcionamento do sistema
from pydantic import BaseModel

# LangChain e LangGraph - Framework para criação de agentes e workflows
from langchain_ollama import ChatOllama  # Interface para modelos Ollama
from langgraph.graph import START, END, StateGraph  # Componentes para criar grafos de estados
from langgraph.types import Send  # Tipo para envio de mensagens entre nós
from pydantic.v1.typing import display_as_type
from tavily import TavilyClient  # Cliente para pesquisa web via API Tavily

# Importação dos módulos locais
import prompts  # Templates de prompts para os LLMs
from schemas import *  # Estruturas de dados (ReportState, QueryResult)
from prompts import *  # Prompts específicos para cada etapa

# Carregamento de variáveis de ambiente (API keys)
from dotenv import load_dotenv
load_dotenv()

# Interface web com Streamlit
import streamlit as st

# Configuração dos modelos LLM
# Modelo menor para tarefas simples (geração de queries)
llm = ChatOllama(model="llama3.2:1b")
# Modelo maior para raciocínio complexo (resposta final)
llm_reasoning = ChatOllama(model="llama3.2:3b")

# ============================================================================
# NÓDULOS DO LANGGRAPH - Cada função representa um agente/etapa do workflow
# ============================================================================

def build_first_queries(state: ReportState):
    """
    PRIMEIRO NÓDULO: Gerador de Queries de Pesquisa
    
    Esta função é o ponto de entrada do workflow. Ela recebe a pergunta do usuário
    e gera múltiplas queries de pesquisa para obter informações abrangentes.
    
    Args:
        state (ReportState): Estado atual contendo a pergunta do usuário
        
    Returns:
        dict: Dicionário com lista de queries geradas
    """
    # Classe para forçar estrutura específica na resposta do LLM
    class QueryList(BaseModel):
        queries: List[str] = []  # Lista obrigatória de strings (queries de pesquisa)

    # Extrai a pergunta original do estado compartilhado
    user_input = state.user_input

    # Formata o prompt substituindo a variável {user_input}
    prompt = build_queries.format(user_input=user_input)
    
    # Configura LLM para retornar APENAS no formato QueryList (structured output)
    query_llm = llm.with_structured_output(QueryList)
    
    # Executa o modelo e obtém as queries estruturadas
    result = query_llm.invoke(prompt)

    # Retorna as queries para serem usadas pelos próximos nódulos
    return {"queries": result.queries}

def spawn_researchers(state: ReportState):
    """
    FUNÇÃO DE ROTEAMENTO: Distribuidor de Pesquisas Paralelas
    
    Esta função implementa o padrão "fan-out" do LangGraph, criando múltiplas
    execuções paralelas do nódulo 'single_search' - uma para cada query gerada.
    
    Args:
        state (ReportState): Estado contendo as queries a serem pesquisadas
        
    Returns:
        List[Send]: Lista de objetos Send para execução paralela
    """
    # Cria uma instância Send para cada query, permitindo execução paralela
    # Cada Send direciona para o nódulo 'single_search' com uma query específica
    return [Send("single_search", {"query": query}) for query in state.queries]

def single_search(state: dict):
    """
    SEGUNDO NÓDULO: Pesquisador Individual (Execução Paralela)
    
    Esta função executa uma pesquisa web individual usando a API Tavily,
    extrai o conteúdo da página e gera um resumo focado na query específica.
    Múltiplas instâncias desta função rodam em paralelo.
    
    Args:
        state (dict): Dicionário contendo a query específica para pesquisa
        
    Returns:
        dict: Resultado da pesquisa estruturado em QueryResult
    """
    # Extrai a query específica enviada pelo spawn_researchers
    query = state["query"]
    
    # Inicializa cliente Tavily para pesquisa web
    tavily_client = TavilyClient()
    
    # Executa pesquisa web (máximo 1 resultado por query)
    results = tavily_client.search(query, max_results=1, include_raw_content=False)

    # Obtém URL do primeiro resultado
    url = results["results"][0]["url"]
    
    # Extrai conteúdo completo da página
    url_extraction = tavily_client.extract(url)

    # Verifica se a extração foi bem-sucedida
    if len(url_extraction["results"]) > 0:
        # Obtém conteúdo bruto da página
        raw_content = url_extraction["results"][0]["raw_content"]
        
        # Formata prompt para resumir conteúdo relevante à query
        prompt = resume_search.format(user_input=query, search_results=raw_content)

        # Gera resumo usando LLM menor (mais rápido)
        llm_result = llm.invoke(prompt)

        # Estrutura resultado da pesquisa
        query_result = QueryResult(
            title=results["results"][0]["title"],
            url=url,
            resume=llm_result.content
        )
        
        # Retorna resultado para agregação no estado global
        return {"queries_results": [query_result]}

def final_write(state: ReportState):
    """
    TERCEIRO NÓDULO: Compilador de Resposta Final
    
    Esta função agrega todos os resultados das pesquisas paralelas e gera
    uma resposta final abrangente usando o modelo LLM mais potente.
    Implementa o padrão "fan-in" do LangGraph.
    
    Args:
        state (ReportState): Estado contendo todos os resultados das pesquisas
        
    Returns:
        dict: Resposta final formatada com referências
    """
    # Inicializa strings para compilar resultados e referências
    search_results = ""
    references = ""

    # Itera sobre todos os resultados das pesquisas paralelas
    for i, result in enumerate(state.queries_results):
        # Formata cada resultado de pesquisa de forma estruturada
        search_results += f"{i+1}\n\n"
        search_results += f"Title: {result.title}\n"
        search_results += f"URL: {result.url}\n"
        search_results += f"Resume: {result.resume}\n"
        search_results += f"===========\n\n"
        
        # Constrói lista de referências numeradas
        references += f"[{i+1}] {result.title} - {result.url}\n"

    # Formata prompt final com pergunta original e todos os resultados
    prompt = build_final_response.format(
        user_input=state.user_input, 
        search_results=search_results
    )
    
    # Usa modelo mais potente para raciocínio complexo e síntese
    llm_result = llm_reasoning.invoke(prompt)
    
    # Combina resposta do LLM com referências formatadas
    final_response = llm_result.content + "\n\n References: \n" + references

    # Retorna resposta final para o estado
    return {"final_response": final_response}


# ============================================================================
# CONFIGURAÇÃO DO LANGGRAPH - Definição do workflow e conexões
# ============================================================================

# Cria o construtor do grafo com o estado compartilhado ReportState
builder = StateGraph(ReportState)

# Adiciona os nódulos (funções) ao grafo
builder.add_node("build_first_queries", build_first_queries)  # Gerador de queries
builder.add_node("single_search", single_search)              # Pesquisador paralelo
builder.add_node("final_write", final_write)                  # Compilador final

# Define as conexões (edges) entre os nódulos
builder.add_edge(START, "build_first_queries")  # Inicia com geração de queries

# Conexão condicional: distribui queries para pesquisas paralelas
builder.add_conditional_edges(
    "build_first_queries",    # Nódulo de origem
    spawn_researchers,         # Função de roteamento
    ["single_search"]         # Nódulos de destino
)

# Conecta pesquisas ao compilador final
builder.add_edge("single_search", "final_write")

# Finaliza o workflow
builder.add_edge("final_write", END)

# Compila o grafo em um objeto executável
graph = builder.compile()

# ============================================================================
# INTERFACE STREAMLIT - Aplicação web para interação com o usuário
# ============================================================================

if __name__ == "__main__":
    # Visualização opcional do grafo (requer IPython)
    try:
        from IPython.display import Image, display
        display(Image(graph.get_graph().draw_mermaid_png()))
    except ImportError:
        pass  # IPython não disponível em ambiente Streamlit

    # Configuração da interface web
    st.title("🔍 Perplexity Clone - Ollama + LangGraph")
    st.markdown("*Pesquisa inteligente com IA local usando Ollama e busca web via Tavily*")
    
    # Campo de entrada para a pergunta do usuário
    user_input = st.text_input(
        "Faça sua pergunta:", 
        placeholder="Ex: Quais são as últimas novidades em IA?"
    )

    # Botão para iniciar a pesquisa
    if st.button("🚀 Pesquisar", type="primary"):
        if user_input.strip():  # Verifica se há input válido
            # Interface de progresso durante execução
            with st.status("🔄 Processando sua pergunta...", expanded=True) as status:
                st.write("📝 Gerando queries de pesquisa...")
                
                # Executa o workflow LangGraph em modo stream para feedback em tempo real
                for output in graph.stream(
                    {"user_input": user_input},
                    stream_mode="debug"  # Modo debug para acompanhar execução
                ):
                    # Mostra progresso de cada nódulo executado
                    if output["type"] == "task_result":
                        node_name = output['payload']['name']
                        st.write(f"✅ Executando: {node_name}")
                
                status.update(label="✅ Pesquisa concluída!", state="complete")
            
            # Extrai e exibe a resposta final
            try:
                # Obtém resultado final do último output
                final_result = graph.invoke({"user_input": user_input})
                final_response = final_result.get("final_response", "Erro ao gerar resposta")
                
                # Exibe resposta formatada
                st.markdown("### 📋 Resposta:")
                st.markdown(final_response)
                
            except Exception as e:
                st.error(f"❌ Erro durante processamento: {str(e)}")
        else:
            st.warning("⚠️ Por favor, digite uma pergunta válida.")
 

